# ER Model — Multi-Platform E-Commerce Management System (MPEMS)

## Complete Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                              ╔═══════════════╗                                          │
│                              ║   companies   ║                                          │
│                              ║───────────────║                                          │
│                              ║ PK id         ║                                          │
│                              ║ name          ║                                          │
│                              ║ legal_name    ║                                          │
│                              ║ gstin (UQ)    ║                                          │
│                              ║ pan           ║                                          │
│                              ║ address       ║                                          │
│                              ║ contact_email ║                                          │
│                              ║ contact_phone ║                                          │
│                              ║ bank_details  ║                                          │
│                              ║ is_active     ║                                          │
│                              ╚═══════╤═══════╝                                          │
│                                      │                                                  │
│                    ┌─────────────────┼─────────────────────┐                            │
│                    │ 1:N             │ 1:N                  │ 1:N                        │
│                    ▼                 ▼                      ▼                            │
│          ╔═══════════════╗  ╔════════════════╗    ╔══════════════════╗                   │
│          ║  app_users    ║  ║  distributors  ║    ║    products      ║                   │
│          ║───────────────║  ║────────────────║    ║──────────────────║                   │
│          ║ PK id         ║  ║ PK id          ║    ║ PK id            ║                   │
│          ║ FK company_id ║  ║ FK company_id  ║    ║ FK company_id    ║                   │
│          ║ FK distrib_id ║  ║ name           ║    ║ sku (UQ)         ║                   │
│          ║ username (UQ) ║  ║ legal_name     ║    ║ name             ║                   │
│          ║ email (UQ)    ║  ║ gstin (UQ)     ║    ║ FK category_id   ║                   │
│          ║ password_hash ║  ║ region         ║    ║ mrp              ║                   │
│          ║ full_name     ║  ║ contact_person ║    ║ distributor_price║                   │
│          ║ role (ENUM)   ║  ║ credit_limit   ║    ║ cost_price       ║                   │
│          ║ assigned_plat ║  ║ payment_terms  ║    ║ weight, dims     ║                   │
│          ║ is_active     ║  ║ status (ENUM)  ║    ║ hsn_code         ║                   │
│          ╚═══════════════╝  ║ bank_details   ║    ║ gst_rate         ║                   │
│                             ╚═══════╤════════╝    ║ status (ENUM)    ║                   │
│                                     │             ╚════════╤═════════╝                   │
│                 ┌───────────────┬────┴─────────┐           │                             │
│                 │ 1:N           │ 1:N           │ 1:N       │ 1:N                         │
│                 ▼               ▼               ▼           ▼                             │
│   ╔══════════════════╗ ╔═══════════════════╗ ╔══════════════════════╗ ╔════════════════╗ │
│   ║  distributor_    ║ ║ platform_         ║ ║  stock_transfers     ║ ║ product_       ║ │
│   ║  warehouses      ║ ║ connections       ║ ║──────────────────────║ ║ variants       ║ │
│   ║──────────────────║ ║───────────────────║ ║ PK id                ║ ║────────────────║ │
│   ║ PK id            ║ ║ PK id             ║ ║ sto_number (UQ)      ║ ║ PK id          ║ │
│   ║ FK distributor_id║ ║ FK distributor_id ║ ║ FK company_id        ║ ║ FK product_id  ║ │
│   ║ name             ║ ║ FK platform_id    ║ ║ FK distributor_id    ║ ║ variant_sku(UQ)║ │
│   ║ address          ║ ║ seller_id         ║ ║ status (ENUM)        ║ ║ size           ║ │
│   ║ pincode          ║ ║ credentials(enc)  ║ ║ subtotal             ║ ║ color          ║ │
│   ║ is_default       ║ ║ sync_frequency    ║ ║ gst_amount           ║ ║ mrp            ║ │
│   ║ is_active        ║ ║ auto_accept       ║ ║ total_amount         ║ ║ distrib_price  ║ │
│   ╚════════╤═════════╝ ║ inventory_buffer  ║ ║ payment_terms        ║ ║ barcode        ║ │
│            │           ║ FK warehouse_id   ║ ║ invoice_number       ║ ╚════════════════╝ │
│            │           ║ status (ENUM)     ║ ║ tracking_number      ║                    │
│            │           ║ last_sync_at      ║ ║ FK created_by        ║                    │
│            │           ║ UQ(dist,platform) ║ ║ FK approved_by       ║                    │
│            │           ╚═════════╤═════════╝ ╚═══════════╤══════════╝                    │
│            │                     │                        │                               │
│            │           ┌─────────┼──────────┐             │ 1:N                           │
│            │           │ 1:N     │ 1:N      │ 1:N         ▼                               │
│            │           │         │          │    ╔══════════════════════╗                 │
│            │           │         │          │    ║ stock_transfer_items ║                 │
│            │           │         │          │    ║──────────────────────║                 │
│            │           │         │          │    ║ PK id                ║                 │
│            │           │         │          │    ║ FK stock_transfer_id ║                 │
│            │           │         │          │    ║ FK product_id        ║                 │
│            │           │         │          │    ║ FK variant_id        ║                 │
│            │           │         │          │    ║ quantity_sent        ║                 │
│            │           │         │          │    ║ quantity_received    ║                 │
│            │           │         │          │    ║ quantity_damaged     ║                 │
│            │           │         │          │    ║ unit_price           ║                 │
│            │           │         │          │    ║ gst_rate             ║                 │
│            │           │         │          │    ║ line_total           ║                 │
│            │           │         │          │    ╚══════════════════════╝                 │
│            │           │         │          │                                             │
│            │           ▼         │          ▼                                             │
│            │  ╔═══════════════╗  │  ╔═════════════════════╗                              │
│            │  ║  platform_    ║  │  ║  settlement_        ║                              │
│            │  ║  listings     ║  │  ║  transactions       ║                              │
│            │  ║───────────────║  │  ║─────────────────────║                              │
│            │  ║ PK id         ║  │  ║ PK id               ║                              │
│            │  ║ FK plat_conn  ║  │  ║ FK plat_conn_id     ║                              │
│            │  ║ FK product_id ║  │  ║ FK distributor_id   ║                              │
│            │  ║ FK variant_id ║  │  ║ settlement_id       ║                              │
│            │  ║ platform_pid  ║  │  ║ settlement_date     ║                              │
│            │  ║ selling_price ║  │  ║ gross_amount        ║                              │
│            │  ║ listed_stock  ║  │  ║ total_fees          ║                              │
│            │  ║ status (ENUM) ║  │  ║ net_amount          ║                              │
│            │  ║ UQ(conn,prod, ║  │  ║ expected_amount     ║                              │
│            │  ║    variant)   ║  │  ║ discrepancy         ║                              │
│            │  ╚═══════════════╝  │  ║ status (ENUM)       ║                              │
│            │                     │  ╚═════════════════════╝                              │
│            │                     │                                                       │
│            │                     ▼  1:N                                                  │
│            │            ╔═══════════════════╗                                            │
│            │            ║     orders        ║                                            │
│            │            ║───────────────────║                                            │
│            │            ║ PK id             ║                                            │
│            │            ║ order_number (UQ) ║                                            │
│            │            ║ FK plat_conn_id   ║                                            │
│            │            ║ platform_order_id ║                                            │
│            │            ║ FK distributor_id ║                                            │
│            │            ║ FK warehouse_id   ║◄────────────────────┐                     │
│            │            ║ customer_name     ║                     │                      │
│            │            ║ customer_address  ║                     │                      │
│            │            ║ order_date        ║                     │  FK                   │
│            │            ║ ship_by_date      ║                     │                      │
│            │            ║ status (ENUM)     ║                     │                      │
│            │            ║ total_amount      ║                     │                      │
│            │            ║ platform_fees_tot ║                     │                      │
│            │            ║ net_receivable    ║                     │                      │
│            │            ║ tracking_number   ║                     │                      │
│            │            ║ FK fulfilled_by   ║                     │                      │
│            │            ║ UQ(conn,plat_oid) ║                     │                      │
│            │            ╚════════╤══════════╝                     │                      │
│            │                     │                                │                      │
│            │           ┌─────────┼──────────┐                    │                      │
│            │           │ 1:N     │ 1:N      │ 1:N                │                      │
│            │           ▼         ▼          ▼                    │                      │
│            │  ╔═════════════╗╔══════════╗╔═══════════════╗       │                      │
│            │  ║ order_items ║║ platform ║║   returns     ║       │                      │
│            │  ║─────────────║║ _fees    ║║───────────────║       │                      │
│            │  ║ PK id       ║║──────────║║ PK id         ║       │                      │
│            │  ║ FK order_id ║║ PK id    ║║ FK order_id   ║       │                      │
│            │  ║ FK product  ║║ FK order ║║ FK plat_conn  ║       │                      │
│            │  ║ FK variant  ║║ fee_type ║║ FK distrib_id ║       │                      │
│            │  ║ plat_item_id║║ (ENUM)   ║║ plat_return_id║       │                      │
│            │  ║ quantity    ║║ amount   ║║ return_type   ║       │                      │
│            │  ║ sell_price  ║║ descript.║║ reason        ║       │                      │
│            │  ║ line_total  ║╚══════════╝║ status (ENUM) ║       │                      │
│            │  ╚═════════════╝            ║ refund_amount ║       │                      │
│            │                             ║ condition     ║       │                      │
│            │                             ║ FK inspected  ║       │                      │
│            │                             ╚═══════╤═══════╝       │                      │
│            │                                     │ 1:N           │                      │
│            │                                     ▼               │                      │
│            │                            ╔═══════════════╗        │                      │
│            │                            ║ return_items  ║        │                      │
│            │                            ║───────────────║        │                      │
│            │                            ║ PK id         ║        │                      │
│            │                            ║ FK return_id  ║        │                      │
│            │                            ║ FK order_item ║        │                      │
│            │                            ║ FK product_id ║        │                      │
│            │                            ║ FK variant_id ║        │                      │
│            │                            ║ qty_returned  ║        │                      │
│            │                            ║ qty_restocked ║        │                      │
│            │                            ║ condition     ║        │                      │
│            │                            ╚═══════════════╝        │                      │
│            │                                                     │                      │
│            ▼  1:N                                                │                      │
│  ╔══════════════════════╗                                        │                      │
│  ║ distributor_         ║                                        │                      │
│  ║ inventory            ║────────────────────────────────────────┘                      │
│  ║──────────────────────║                                                               │
│  ║ PK id                ║         ╔══════════════════╗                                  │
│  ║ FK distributor_id    ║         ║    inventory     ║  (Company Warehouse)              │
│  ║ FK warehouse_id      ║         ║──────────────────║                                  │
│  ║ FK product_id        ║         ║ PK id            ║                                  │
│  ║ FK variant_id        ║         ║ FK company_id    ║                                  │
│  ║ quantity             ║         ║ FK product_id    ║                                  │
│  ║ reserved_quantity    ║         ║ FK variant_id    ║                                  │
│  ║ min_threshold        ║         ║ quantity         ║                                  │
│  ║ location             ║         ║ reserved_qty     ║                                  │
│  ║ UQ(wh,prod,variant)  ║         ║ min_threshold    ║                                  │
│  ╚══════════════════════╝         ║ location         ║                                  │
│                                   ║ UQ(co,prod,var)  ║                                  │
│                                   ╚══════════════════╝                                  │
│                                                                                         │
│  ═══════════════════════════════════════════════════════════════                         │
│  REFERENCE / LOOKUP TABLES:                                                             │
│  ═══════════════════════════════════════════════════════════════                         │
│                                                                                         │
│  ╔═══════════════════╗       ╔════════════════════╗                                     │
│  ║    platforms       ║       ║ product_categories ║                                     │
│  ║───────────────────║       ║────────────────────║                                     │
│  ║ PK id             ║       ║ PK id              ║                                     │
│  ║ code (UQ)         ║       ║ FK company_id      ║                                     │
│  ║ name              ║       ║ name               ║                                     │
│  ║ api_base_url      ║       ║ FK parent_cat_id   ║ (self-referencing)                  │
│  ║ commission_default║       ║ hsn_code           ║                                     │
│  ║ return_window     ║       ║ gst_rate           ║                                     │
│  ║ settlement_cycle  ║       ╚════════════════════╝                                     │
│  ╚═══════════════════╝                                                                  │
│                                                                                         │
│  ╔═══════════════════════╗                                                              │
│  ║ distributor_payments  ║                                                              │
│  ║───────────────────────║                                                              │
│  ║ PK id                 ║                                                              │
│  ║ FK distributor_id     ║                                                              │
│  ║ FK stock_transfer_id  ║                                                              │
│  ║ amount                ║                                                              │
│  ║ payment_method (ENUM) ║                                                              │
│  ║ payment_reference     ║                                                              │
│  ║ payment_date          ║                                                              │
│  ║ status (ENUM)         ║                                                              │
│  ║ FK confirmed_by       ║                                                              │
│  ╚═══════════════════════╝                                                              │
│                                                                                         │
│  ═══════════════════════════════════════════════════════════════                         │
│  CROSS-CUTTING / AUDIT TABLES (append-only logs):                                      │
│  ═══════════════════════════════════════════════════════════════                         │
│                                                                                         │
│  ╔══════════════════╗ ╔═══════════════╗ ╔═══════════════╗ ╔═════════════╗               │
│  ║  inventory_log   ║ ║  audit_log    ║ ║  sync_log     ║ ║notifications║               │
│  ║──────────────────║ ║───────────────║ ║───────────────║ ║─────────────║               │
│  ║ PK id            ║ ║ PK id (BIGINT)║ ║ PK id         ║ ║ PK id       ║               │
│  ║ inventory_level  ║ ║ FK user_id    ║ ║ FK plat_conn  ║ ║ FK user_id  ║               │
│  ║ FK distrib_id    ║ ║ distributor_id║ ║ sync_type     ║ ║ type        ║               │
│  ║ FK product_id    ║ ║ platform_id   ║ ║ direction     ║ ║ title       ║               │
│  ║ action (ENUM)    ║ ║ action        ║ ║ status (ENUM) ║ ║ message     ║               │
│  ║ old_quantity     ║ ║ entity_type   ║ ║ records_proc  ║ ║ severity    ║               │
│  ║ new_quantity     ║ ║ entity_id     ║ ║ records_fail  ║ ║ ref_type    ║               │
│  ║ change_quantity  ║ ║ old_value(J)  ║ ║ error_message ║ ║ ref_id      ║               │
│  ║ reason           ║ ║ new_value(J)  ║ ║ started_at    ║ ║ is_read     ║               │
│  ║ ref_type         ║ ║ ip_address    ║ ║ completed_at  ║ ╚═════════════╝               │
│  ║ ref_id           ║ ║ APPEND-ONLY   ║ ╚═══════════════╝                               │
│  ║ FK performed_by  ║ ╚═══════════════╝                   ╔═════════════╗               │
│  ║ APPEND-ONLY      ║                                     ║ email_queue ║               │
│  ╚══════════════════╝                                     ║─────────────║               │
│                                                           ║ PK id       ║               │
│                                                           ║ to_email    ║               │
│                                                           ║ subject     ║               │
│                                                           ║ body        ║               │
│                                                           ║ status(ENUM)║               │
│                                                           ║ retry_count ║               │
│                                                           ╚═════════════╝               │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Relationship Summary Table

| # | Parent Entity | Child Entity | Relationship | Foreign Key | Description |
|---|--------------|-------------|-------------|-------------|-------------|
| 1 | companies | app_users | 1:N | app_users.company_id | Company has many users |
| 2 | companies | distributors | 1:N | distributors.company_id | Company has many distributors |
| 3 | companies | products | 1:N | products.company_id | Company owns product catalog |
| 4 | companies | product_categories | 1:N | product_categories.company_id | Company defines categories |
| 5 | companies | inventory | 1:N | inventory.company_id | Company warehouse stock |
| 6 | product_categories | product_categories | 1:N (self) | parent_category_id | Nested categories |
| 7 | products | product_variants | 1:N | product_variants.product_id | Product has size/color variants |
| 8 | products | platform_listings | 1:N | platform_listings.product_id | Product listed on platforms |
| 9 | distributors | distributor_warehouses | 1:N | distributor_warehouses.distributor_id | Distributor has warehouses |
| 10 | distributors | platform_connections | 1:N | platform_connections.distributor_id | Distributor connects to platforms |
| 11 | distributors | stock_transfers | 1:N | stock_transfers.distributor_id | Distributor receives stock |
| 12 | distributors | distributor_inventory | 1:N | distributor_inventory.distributor_id | Distributor warehouse stock |
| 13 | distributors | distributor_payments | 1:N | distributor_payments.distributor_id | Distributor pays company |
| 14 | distributors | app_users | 1:N | app_users.distributor_id | Distributor has staff users |
| 15 | platforms | platform_connections | 1:N | platform_connections.platform_id | Platform has many seller accounts |
| 16 | platform_connections | orders | 1:N | orders.platform_connection_id | Connection generates orders |
| 17 | platform_connections | platform_listings | 1:N | platform_listings.platform_connection_id | Connection has listings |
| 18 | platform_connections | settlement_transactions | 1:N | settlement_transactions.platform_connection_id | Connection receives settlements |
| 19 | platform_connections | sync_log | 1:N | sync_log.platform_connection_id | Connection sync history |
| 20 | stock_transfers | stock_transfer_items | 1:N | stock_transfer_items.stock_transfer_id | Transfer has line items |
| 21 | orders | order_items | 1:N | order_items.order_id | Order has line items |
| 22 | orders | platform_fees | 1:N | platform_fees.order_id | Order has fee breakdown |
| 23 | orders | returns | 1:N | returns.order_id | Order may have returns |
| 24 | returns | return_items | 1:N | return_items.return_id | Return has line items |
| 25 | distributor_warehouses | distributor_inventory | 1:N | distributor_inventory.warehouse_id | Warehouse holds stock |
| 26 | distributor_warehouses | orders | 1:N | orders.warehouse_id | Orders fulfilled from warehouse |
| 27 | app_users | notifications | 1:N | notifications.user_id | User receives notifications |
| 28 | app_users | audit_log | 1:N | audit_log.user_id | User actions logged |

---

## Cardinality Rules

| Rule | Description |
|------|-------------|
| Each **company** has 1+ distributors, 1+ products, 1+ users |
| Each **distributor** belongs to exactly 1 company |
| Each **distributor** has 1+ warehouses, 0+ platform connections |
| Each **platform_connection** is unique per (distributor, platform) |
| Each **product** belongs to exactly 1 company, has 0+ variants |
| Each **platform_listing** maps 1 product (or variant) to 1 platform_connection |
| Each **stock_transfer** goes from 1 company to 1 distributor, has 1+ items |
| Each **order** belongs to 1 platform_connection, has 1+ items, 0+ fees, 0+ returns |
| Each **return** belongs to 1 order, has 1+ return_items |
| Each **settlement_transaction** belongs to 1 platform_connection |
| Each **distributor_payment** is from 1 distributor, optionally linked to 1 stock_transfer |
| **inventory_log** and **audit_log** are append-only (no UPDATE/DELETE) |

---

## Entity Count Summary

| Category | Tables | Names |
|----------|--------|-------|
| **Core** | 4 | companies, app_users, product_categories, platforms |
| **Product** | 3 | products, product_variants, platform_listings |
| **Distributor** | 3 | distributors, distributor_warehouses, platform_connections |
| **Primary Sales** | 2 | stock_transfers, stock_transfer_items |
| **Secondary Sales** | 3 | orders, order_items, platform_fees |
| **Inventory** | 3 | inventory, distributor_inventory, inventory_log |
| **Returns** | 2 | returns, return_items |
| **Payments** | 2 | settlement_transactions, distributor_payments |
| **System** | 4 | notifications, email_queue, audit_log, sync_log |
| **Total** | **26 tables** | |
