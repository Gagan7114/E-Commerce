# Data Flow Architecture — MPEMS

> Single source of truth: Self-hosted PostgreSQL.
> SAP and email remain as **sources**, not as live query targets.
> The app reads from one place. ETL workers handle the messy ingestion in the background.

---

## 1. The Problem (Current State)

### What's happening today

```
                                 PROBLEM AREAS
                                 -------------

  +-------------------+
  | Customer email    |    1) Apps Script parses
  | (Purchase Order)  |       email -> writes to Sheet
  +---------+---------+        (fragile, silent failures)
            |
            v
  +-------------------+
  | Google Sheets     |    2) Another Apps Script
  | (intermediate)    |       reads Sheet -> Supabase
  +---------+---------+        (data drift, no logs)
            |
            v
  +-------------------+        +-------------------+
  | Supabase Postgres |        | SAP HANA          |
  | - master_po       |        | - OCRD (vendors)  |
  | - inventory       |        | - OITM (items)    |
  | - secondary sales |        | - OPOR (orders)   |
  +---------+---------+        | - OPCH (invoices) |
            |                  +---------+---------+
            |                            |
            +------------+---------------+
                         |
                         v
              +---------------------+
              | FastAPI backend     |  Queries BOTH on every request
              +---------+-----------+   - slow (HANA latency)
                        |               - expensive (paid quotas)
                        v               - fragile (network deps)
              +---------------------+
              | React frontend      |  Some pages bypass backend
              | + Supabase JS       |  and hit Supabase directly
              +---------------------+
```

### Pain points

| Pain | Root cause | Impact |
|------|------------|--------|
| PO data wrong / missing | 4-hop pipeline: Email -> Apps Script -> Sheet -> Apps Script -> Supabase | Lost orders, manual reconciliation |
| Slow distributor / item pages | Every request hits SAP HANA live | 2-5 sec page loads |
| Two paid services | Supabase + SAP | Recurring cost |
| Mixed read pattern | Frontend sometimes hits Supabase, sometimes backend | Hard to reason about |
| No audit trail | Don't know where a row came from or when it landed | Debugging is guesswork |
| Truck dispatches in localStorage | Frontend-only persistence | Lost on browser clear, no multi-device |

---

## 2. The Solution (Target State)

### Core principle

**Sources stay sources. The app reads from one place.**

You cannot move SAP — your company runs on it. You cannot stop customers emailing POs. But you CAN build one unified store that the app reads from, and let background workers handle the ingestion.

### Target architecture

```
                          SOURCES (you don't control)
   ===========================================================================

   +---------------+   +---------------+   +-----------------+   +-------------+
   | Email POs     |   | SAP HANA      |   | Platform CSV    |   | Other APIs  |
   | (Gmail IMAP)  |   | (read-only)   |   | uploads         |   | (Amazon etc)|
   +-------+-------+   +-------+-------+   +--------+--------+   +------+------+
           |                   |                    |                   |
           |                   |                    |                   |
           v                   v                    v                   v
   +------------------------------------------------------------------------+
   |                    INGESTION LAYER (Python workers)                    |
   |                                                                        |
   |   email_to_pg.py     sap_sync.py        csv_importer.py    api_sync.py |
   |   (cron: */5 min)    (cron: hourly)     (on upload)        (cron: 1h)  |
   |                                                                        |
   |   - retries with backoff                                               |
   |   - structured logging                                                 |
   |   - idempotent (ON CONFLICT)                                           |
   |   - source + synced_at columns on every row                            |
   +-----------------------------------+------------------------------------+
                                       |
                                       v
                      +================================+
                      |       PostgreSQL 16            |    <-- single source of truth
                      |    (self-hosted, 5 USD/mo)     |
                      |                                |
                      |   - master_po                  |
                      |   - inventory_*                |
                      |   - secondary_sales_*          |
                      |   - sap_distributors (cache)   |
                      |   - sap_items (cache)          |
                      |   - sap_orders (cache)         |
                      |   - truck_dispatches  <-- moved from localStorage
                      |   - ingestion_log              |
                      +================================+
                                       ^
                                       |
                                  +----+----+
                                  | FastAPI |     reads ONLY from Postgres
                                  +----+----+     (one exception: live SAP stock)
                                       |
                                       v
                                  +---------+
                                  |  React  |     reads ONLY from FastAPI
                                  +----+----+     (no more direct Supabase)
                                       |
                                       v
                                  +---------+
                                  | Auth:   |     Supabase free tier
                                  | Supabase|     (don't reinvent auth)
                                  +---------+
```

### Why this works

| Today | After |
|-------|-------|
| 4-hop email pipeline with silent failures | 1 Python script with logs and retries |
| Every distributor view = HANA query | Cached copy, refreshed hourly |
| Pay for Supabase data + SAP | Pay only for SAP (you can't avoid it) |
| Don't know where data came from | Every row has `source` + `synced_at` |
| App can't work if Supabase is down | App works as long as Postgres is up |
| Realtime needs Supabase channels | Postgres `LISTEN/NOTIFY` is built-in |

---

## 3. Per-Source Detailed Flow

### 3.1 Email PO ingestion

```
   Customer email hits Gmail
              |
              v
   +----------------------+
   | email_to_pg.py       |  runs every 5 minutes via cron / systemd timer
   |                      |
   |  1. IMAP login       |
   |  2. Fetch UNSEEN     |
   |     SUBJECT "PO"     |
   |  3. For each msg:    |
   |     a. parse body /  |
   |        attachment    |
   |        (PDF, Excel)  |
   |     b. extract:      |
   |        - PO number   |
   |        - platform    |
   |        - SKU + qty   |
   |        - dates       |
   |     c. INSERT INTO   |
   |        master_po     |
   |        ON CONFLICT   |
   |        DO UPDATE     |
   |     d. mark email    |
   |        as Seen       |
   |     e. log to        |
   |        ingestion_log |
   +----------------------+
              |
              v
   +----------------------+
   | PostgreSQL           |
   | master_po table      |
   +----------------------+
```

**Libraries:** `imaplib` (built-in), `pdfplumber` (PDF), `pandas` + `openpyxl` (Excel), `psycopg2-binary` (PG).

**Failure handling:**
- If parsing fails: log to `ingestion_log` with `status='parse_error'` and the raw email — don't mark as Seen, retry next run
- If DB insert fails: don't mark as Seen, retry next run
- Idempotent: same PO number won't duplicate (ON CONFLICT)

### 3.2 SAP HANA sync

```
   +----------------------+
   | sap_sync.py          |  runs hourly via cron
   |                      |
   |  For each table:     |
   |   - OCRD (vendors)   |
   |   - OITM (items)     |
   |   - OPOR (orders)    |
   |   - OPCH (invoices)  |
   |   - OITW (stock)     |
   |                      |
   |  1. SELECT ... FROM  |
   |     OCRD WHERE       |
   |     UpdateDate >     |
   |     last_sync_time   |
   |  2. UPSERT into      |
   |     sap_distributors |
   |  3. update            |
   |     last_sync_time   |
   +----------+-----------+
              |
              v
   +----------------------+        +--------------------+
   | PostgreSQL           | <----- | FastAPI reads here |
   | sap_distributors     |        +--------------------+
   | sap_items            |
   | sap_orders           |
   | sap_invoices         |
   | sap_stock            |
   +----------------------+
```

**Schema example:**
```sql
CREATE TABLE sap_distributors (
    card_code      TEXT PRIMARY KEY,
    card_name      TEXT NOT NULL,
    phone1         TEXT,
    email          TEXT,
    address        TEXT,
    city           TEXT,
    state          TEXT,
    country        TEXT,
    currency       TEXT,
    balance        NUMERIC(18,4),
    credit_line    NUMERIC(18,4),
    gstin          TEXT,
    is_active      BOOLEAN,
    chain          TEXT,         -- for platform mapping
    main_group     TEXT,
    source         TEXT NOT NULL DEFAULT 'sap_hana',
    synced_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sap_distributors_chain ON sap_distributors(chain);
CREATE INDEX idx_sap_distributors_name  ON sap_distributors USING gin (card_name gin_trgm_ops);
```

**One exception:** if you need *live* stock (e.g., during checkout to prevent oversell), call HANA directly. Mark the endpoint `/api/sap/live-stock/...` clearly so future-you knows it's expensive.

### 3.3 Platform CSV imports (manual)

```
   User uploads CSV in
   admin panel
              |
              v
   +----------------------+
   | POST /api/import     |
   |   /platform-csv      |
   |                      |
   | 1. validate columns  |
   | 2. stream parse      |
   | 3. batch INSERT      |
   |    (1000 rows/batch) |
   | 4. return summary    |
   +----------+-----------+
              |
              v
   +----------------------+
   | PostgreSQL           |
   | inventory_<platform> |
   | secondary_<platform> |
   +----------------------+
```

### 3.4 App reads (steady state)

```
   React page mounts
        |
        v
   fetch('/api/...')
        |
        v
   +-------------------+
   | FastAPI route     |
   |                   |
   | psycopg2 query    |
   | from PostgreSQL   |
   +---------+---------+
             |
             v
   +-------------------+
   | PostgreSQL        |  <-- always responds in <100ms
   +-------------------+     because data is local
```

No SAP call. No Supabase JS in the page. Single, predictable path.

### 3.5 Auth (unchanged)

```
   Login form -----> supabase.auth.signInWithPassword
                              |
                              v
                     Supabase Auth (free tier)
                              |
                              v
                     JWT in localStorage
                              |
                              v
                     User redirected to /dashboard
```

Keep Supabase Auth — it's the one thing you should not rebuild.
For deleted-user logout, switch `getSession()` to `getUser()` (validates against server).

---

## 4. Database Schema Plan

### Tables to create in your new Postgres

| Table | Source | Refresh | Notes |
|-------|--------|---------|-------|
| `master_po` | Email parser | Per email arrival | PRIMARY KEY (po_number) |
| `inventory_amazon`, `inventory_blinkit`, `inventory_zepto`, ... | CSV upload / API | On upload | One per platform |
| `secondary_sales_amazon`, `secondary_sales_blinkit`, ... | CSV upload / API | On upload | One per platform |
| `sap_distributors` | SAP HANA | Hourly | UPSERT on card_code |
| `sap_items` | SAP HANA | Hourly | UPSERT on item_code |
| `sap_orders` | SAP HANA | Hourly | UPSERT on doc_entry |
| `sap_invoices` | SAP HANA | Hourly | UPSERT on doc_entry |
| `sap_stock` | SAP HANA | Every 15 min | More frequent — stock changes faster |
| `truck_dispatches` | App user action | Per dispatch | **Move out of localStorage** |
| `ingestion_log` | All ETL workers | Per batch | source, status, rows, error_msg, ran_at |

### Audit columns on every table

```sql
source       TEXT NOT NULL,            -- 'email', 'sap_hana', 'csv_upload', 'manual'
synced_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
source_ref   TEXT,                     -- email msg-id / SAP doc_entry / file name
```

When something looks wrong, you can answer: "Where did this row come from? When?"

---

## 5. Migration Plan (Phased, NOT a Rewrite)

### Phase 0 — Setup (Day 1-2)

- [ ] Provision VPS (Hetzner CX22 ~4 USD/mo or Contabo VPS ~5 USD/mo)
- [ ] Install PostgreSQL 16, configure backups (`pg_dump` daily to Backblaze B2)
- [ ] Set up nginx reverse proxy with TLS (Let's Encrypt)
- [ ] Set up monitoring (UptimeRobot free tier)
- [ ] Create empty schema with `ingestion_log` table

### Phase 1 — Stop the bleeding: PO email pipeline (Week 1)

- [ ] Write `email_to_pg.py` for the most common PO format first
- [ ] Test against last week of emails (don't mark Seen during test)
- [ ] Deploy as systemd timer
- [ ] Run in parallel with old Sheets pipeline for 1 week
- [ ] Compare outputs — fix discrepancies
- [ ] Once 100% match: kill the Sheets/Apps Script pipeline

### Phase 2 — SAP cache layer (Week 2)

- [ ] Create `sap_*` tables in Postgres
- [ ] Write `sap_sync.py` — start with `sap_distributors`
- [ ] Add new endpoint `/api/v2/distributors` that reads from Postgres
- [ ] Switch frontend `sapAPI.getDistributors()` to v2 endpoint
- [ ] Repeat for items, orders, invoices, stock
- [ ] Keep old `/api/sap/*` endpoints alive for 1 week as fallback
- [ ] Once stable: delete old endpoints

### Phase 3 — Migrate Supabase data tables (Week 3-4)

- [ ] For each Supabase table: create equivalent in Postgres
- [ ] One-time copy: `pg_dump` from Supabase, `psql` into your DB
- [ ] Update FastAPI dashboard / platform routes to use psycopg2 (your DB) instead of supabase httpx wrapper
- [ ] Update Dashboard.jsx to call `dashboardAPI.*` (already defined, just unused) instead of supabase-js direct
- [ ] Test, then drop the Supabase data tables

### Phase 4 — Move truck dispatches out of localStorage (Week 4)

- [ ] Create `truck_dispatches` table in Postgres
- [ ] Add `POST /api/dispatches` and `GET /api/dispatches/:slug` endpoints
- [ ] Migrate `DispatchContext.jsx` to call API instead of localStorage
- [ ] Add a one-time "import from localStorage" button for existing users

### Phase 5 — Cleanup (Week 5)

- [ ] Delete unused Apps Scripts
- [ ] Archive old Google Sheets (don't delete — keep as historical record)
- [ ] Decide: keep Supabase free tier for auth only, or migrate to Auth.js / Clerk
- [ ] Update this document with lessons learned

**Rule:** every phase must end with a working app. No "we'll fix it next week" gaps.

---

## 6. Cost Comparison

### Today (estimate)

| Item | Cost/mo |
|------|---------|
| Supabase Pro (if over free tier) | 25 USD |
| SAP HANA license | (company expense) |
| Google Workspace (Sheets / Apps Script) | (company expense) |
| **Your direct cost** | **~25 USD/mo** |

### Proposed

| Item | Cost/mo |
|------|---------|
| Hetzner CX22 VPS (Postgres + FastAPI + ETL) | 4 USD |
| Backblaze B2 backup storage (~5GB) | 0.50 USD |
| Domain + DNS | 1 USD |
| Supabase free tier (auth only) | 0 USD |
| SAP HANA license | (company expense) |
| **Your direct cost** | **~6 USD/mo** |

Savings: ~19 USD/mo, plus a much more reliable system.

If you outgrow the VPS (>500K rows, >100 concurrent users), upgrade to Hetzner CX42 (8 USD/mo) or move Postgres to Neon ($19/mo for 10GB).

---

## 7. Tech Stack (Final)

| Layer | Choice | Why |
|-------|--------|-----|
| Database | PostgreSQL 16 | Relational data, free, battle-tested |
| Backend | FastAPI (existing) | Already in use, fast |
| Frontend | React + Vite (existing) | No change |
| Auth | Supabase Auth free tier | Don't reinvent auth |
| ETL workers | Python scripts + cron / systemd | Simple, no Airflow needed at this scale |
| Email parsing | imaplib + pdfplumber + pandas | All free, all stable |
| SAP connector | hdbcli (existing) | Already in use |
| Hosting | Hetzner / Contabo VPS | Cheapest reliable option |
| Backups | pg_dump -> Backblaze B2 | Cheap, S3-compatible |
| Monitoring | UptimeRobot + pg_stat_statements | Free, sufficient for this scale |

---

## 8. What NOT to Do

- **Do not** try to remove SAP. Your company runs on it. You can only mirror it.
- **Do not** build your own auth from scratch. Security bugs are too easy.
- **Do not** use MongoDB or any NoSQL. Your data has joins. Use Postgres.
- **Do not** introduce Airflow / dbt / Kafka. Overkill for this scale. Cron is fine.
- **Do not** migrate everything in one weekend. Phase it.
- **Do not** keep the Google Sheets middle step "just in case" — kill it cleanly once Phase 1 is verified.
- **Do not** let the frontend talk directly to Postgres. Always go through FastAPI (auth, validation, audit).

---

## 9. Open Questions to Resolve

Before starting Phase 1, decide:

1. **Email account for ingestion** — dedicated mailbox or shared? IMAP credentials in env file or secret manager?
2. **PO email formats** — how many distinct formats? (one parser per format vs. one regex-based parser)
3. **SAP HANA permissions** — does the read user have access to all needed tables? Any rate limits?
4. **VPS region** — closest to your team / SAP server for low latency
5. **Supabase free tier limits** — current MAU and DB size? Need to know before relying on free tier
6. **Backup retention** — 7 days? 30 days? Affects B2 cost slightly

---

## 10. Quick Reference Diagrams

### Steady-state read path

```
Browser  ->  React  ->  fetch /api/...  ->  FastAPI  ->  psycopg2  ->  PostgreSQL
                                                                            |
                                                                       (responds in <100ms)
```

### Steady-state write path (PO arrives)

```
Customer email  ->  Gmail  ->  cron fires every 5 min  ->  email_to_pg.py
                                                                  |
                                                                  v
                                               psycopg2 INSERT INTO master_po
                                                                  |
                                                                  v
                                                            PostgreSQL
                                                                  |
                                                                  v
                                          (next time user opens dashboard, PO is there)
```

### Failure case (SAP down, hourly sync fails)

```
sap_sync.py runs  ->  HANA timeout  ->  log to ingestion_log (status='hana_unreachable')
                                                  |
                                                  v
                                  next hour: try again, succeeds
                                                  |
                                                  v
                       app keeps working entire time (reads cached Postgres data)
```

This is the whole point: **cache decouples app uptime from source uptime**.

---

*Document version 1 — created during initial architecture review. Update at the end of each migration phase.*
