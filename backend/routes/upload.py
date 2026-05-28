"""
Generic data upload endpoint for the uploader tool.
Supports batch INSERT and UPSERT (ON CONFLICT DO UPDATE).
"""

from datetime import date, datetime
from decimal import Decimal
from difflib import SequenceMatcher

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from db.postgres_client import get_conn, put_conn
from permissions import require_perm

router = APIRouter(
    prefix="/api/upload",
    tags=["Upload"],
    dependencies=[Depends(require_perm("upload.use"))],
)

# Tables the uploader is allowed to write to
UPLOAD_ALLOWED_TABLES = [
    # Inventory
    "blinkit_inventory", "zepto_inventory", "swiggy_inventory",
    "bigbasket_inventory", "jiomart_inventory", "amazon_inventory",
    # Secondary sells
    "blinkitSec", "zeptoSec", "swiggySec", "flipkartSec",
    "jiomartSec", "bigbasketSec", "amazon_sec_daily", "amazon_sec_range",
    "fk_grocery", "flipkart_grocery_master",
    # Truck loading
    "blinkit_truck_loading",
]


class UploadRequest(BaseModel):
    table: str
    data: List[dict]
    unique_key: Optional[str] = None  # comma-separated conflict columns
    upsert: bool = True


class FkGroceryMasterRequest(BaseModel):
    data: List[dict]
    upsert: bool = True


def _as_decimal(value, default=Decimal("0")):
    if value is None or value == "":
        return default
    try:
        return Decimal(str(value).replace(",", ""))
    except Exception:
        return default


def _parse_date(value):
    if isinstance(value, date):
        return value
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def _format_dmy(value):
    return value.strftime("%d-%m-%Y") if value else None


def _month_start(d):
    return d.replace(day=1).isoformat()


def _month_name(d):
    return d.month


def _ensure_fk_grocery_master(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS "flipkart_grocery_master" (
            "date" VARCHAR(10),
            "sku_id" VARCHAR,
            "brand" VARCHAR,
            "qty" NUMERIC,
            "per_ltr" NUMERIC,
            "per_ltr_unit" VARCHAR,
            "uom" VARCHAR,
            "ltr_sold" NUMERIC,
            "real_date" DATE,
            "month" INTEGER,
            "year" INTEGER,
            "item" VARCHAR,
            "landing_rate" NUMERIC,
            "basic_rate" NUMERIC,
            "sale_amt_inclusive" NUMERIC,
            "sale_amt_exclusive" NUMERIC,
            "category" VARCHAR,
            "sub_category" VARCHAR,
            "item_head" VARCHAR
        )
        """
    )
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS flipkart_grocery_master_sku_date_uq
        ON "flipkart_grocery_master" ("sku_id", "real_date")
        """
    )


def _get_master_row(cur, sku_id):
    cur.execute(
        """
        SELECT format_sku_code, product_name, item, category, sub_category,
               per_unit, item_head, brand, uom, per_unit_value
        FROM master_sheet
        WHERE format_sku_code = %s
        LIMIT 1
        """,
        (sku_id,),
    )
    return cur.fetchone()


def _get_price_row(cur, sku_id, product_name, real_date):
    target_month = _month_start(real_date)
    params = [sku_id, target_month]
    name_clause = ""
    if product_name:
        name_clause = " OR LOWER(TRIM(sku_name)) = LOWER(TRIM(%s))"
        params.insert(1, product_name)

    cur.execute(
        f"""
        SELECT landing_rate, basic_rate
        FROM monthly_landing_rate
        WHERE UPPER(TRIM(format)) = 'FLIPKART GROCERY'
          AND (sku_code = %s{name_clause})
          AND month = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        tuple(params),
    )
    row = cur.fetchone()
    if row:
        return row

    params = [sku_id]
    name_clause = ""
    if product_name:
        name_clause = " OR LOWER(TRIM(sku_name)) = LOWER(TRIM(%s))"
        params.append(product_name)

    cur.execute(
        f"""
        SELECT landing_rate, basic_rate
        FROM monthly_landing_rate
        WHERE UPPER(TRIM(format)) = 'FLIPKART GROCERY'
          AND (sku_code = %s{name_clause})
        ORDER BY month DESC, created_at DESC
        LIMIT 1
        """,
        tuple(params),
    )
    row = cur.fetchone()
    if row:
        return row

    cur.execute(
        """
        SELECT sku_code, sku_name, landing_rate, basic_rate
        FROM monthly_landing_rate
        WHERE UPPER(TRIM(format)) = 'FLIPKART GROCERY'
        ORDER BY month DESC, created_at DESC
        """
    )
    candidates = cur.fetchall()

    def norm(value):
        return "".join(ch for ch in str(value or "").upper() if ch.isalnum()).replace("O", "0")

    sku_norm = norm(sku_id)
    product_norm = norm(product_name)
    best = None
    best_score = 0
    for cand_sku, cand_name, landing_rate, basic_rate in candidates:
        sku_score = SequenceMatcher(None, sku_norm, norm(cand_sku)).ratio()
        name_score = SequenceMatcher(None, product_norm, norm(cand_name)).ratio() if product_norm else 0
        score = max(sku_score, name_score)
        if score > best_score:
            best_score = score
            best = (landing_rate, basic_rate)

    return best if best_score >= 0.88 else None


@router.post("/batch")
async def batch_upload(req: UploadRequest):
    if req.table not in UPLOAD_ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail=f"Table '{req.table}' is not allowed for upload")

    if not req.data or len(req.data) == 0:
        return {"success": 0, "failed": 0, "error": None}

    conn = get_conn()
    try:
        success = 0
        failed = 0
        last_error = None

        # Get column names from first row
        columns = list(req.data[0].keys())
        quoted_cols = [f'"{c}"' for c in columns]
        col_list = ", ".join(quoted_cols)
        placeholders = ", ".join(["%s"] * len(columns))

        # Build upsert clause if needed
        upsert_clause = ""
        if req.upsert and req.unique_key:
            conflict_cols = ", ".join(f'"{c.strip()}"' for c in req.unique_key.split(","))
            update_cols = [f'"{c}" = EXCLUDED."{c}"' for c in columns
                          if c.strip() not in [k.strip() for k in req.unique_key.split(",")]]
            if update_cols:
                upsert_clause = f" ON CONFLICT ({conflict_cols}) DO UPDATE SET {', '.join(update_cols)}"
            else:
                upsert_clause = f" ON CONFLICT ({conflict_cols}) DO NOTHING"

        sql = f'INSERT INTO "{req.table}" ({col_list}) VALUES ({placeholders}){upsert_clause}'

        # Process in batches of 50
        batch_size = 50
        with conn.cursor() as cur:
            for i in range(0, len(req.data), batch_size):
                batch = req.data[i:i + batch_size]
                try:
                    for row in batch:
                        values = [row.get(c) for c in columns]
                        cur.execute(sql, values)
                    conn.commit()
                    success += len(batch)
                except Exception as e:
                    conn.rollback()
                    failed += len(batch)
                    last_error = str(e)

        return {
            "success": success,
            "failed": failed,
            "error": last_error,
        }
    finally:
        put_conn(conn)


@router.post("/fk-grocery-master")
async def upload_fk_grocery_master(req: FkGroceryMasterRequest):
    if not req.data:
        return {"success": 0, "failed": 0, "error": None}

    conn = get_conn()
    try:
        rows = []
        failed = 0
        missing_master = set()
        missing_price = set()
        master_cache = {}
        price_cache = {}

        with conn.cursor() as cur:
            _ensure_fk_grocery_master(cur)

            for row in req.data:
                sku_id = str(row.get("sku_id") or row.get("fsn") or "").strip()
                real_date = _parse_date(row.get("real_date") or row.get("raw_date") or row.get("date"))
                if not sku_id or real_date is None:
                    failed += 1
                    continue

                qty = _as_decimal(row.get("qty"))
                brand = str(row.get("brand") or "").strip() or None
                if sku_id not in master_cache:
                    master_cache[sku_id] = _get_master_row(cur, sku_id)
                master = master_cache[sku_id]
                if not master:
                    missing_master.add(sku_id)

                product_name = master[1] if master else None
                price_key = (sku_id, product_name or "", real_date.replace(day=1))
                if price_key not in price_cache:
                    price_cache[price_key] = _get_price_row(
                        cur, sku_id, product_name, real_date
                    )
                price = price_cache[price_key]
                if not price:
                    missing_price.add(sku_id)

                per_ltr = _as_decimal(master[9] if master else None)
                landing_rate = _as_decimal(price[0] if price else None)
                basic_rate = _as_decimal(price[1] if price else None)

                rows.append(
                    (
                        _format_dmy(real_date),
                        sku_id,
                        brand or (master[7] if master else None),
                        qty,
                        per_ltr,
                        master[5] if master else None,
                        master[8] if master else None,
                        per_ltr * qty,
                        real_date,
                        _month_name(real_date),
                        real_date.year,
                        master[2] if master else None,
                        landing_rate,
                        basic_rate,
                        landing_rate * qty,
                        basic_rate * qty,
                        master[3] if master else None,
                        master[4] if master else None,
                        master[6] if master else None,
                    )
                )

            if not rows:
                conn.rollback()
                return {
                    "success": 0,
                    "failed": failed or len(req.data),
                    "error": "No valid rows to upload",
                }

            insert_sql = """
                INSERT INTO "flipkart_grocery_master" (
                    "date", "sku_id", "brand", "qty", "per_ltr", "per_ltr_unit",
                    "uom", "ltr_sold", "real_date", "month", "year", "item",
                    "landing_rate", "basic_rate", "sale_amt_inclusive",
                    "sale_amt_exclusive", "category", "sub_category", "item_head"
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            if req.upsert:
                insert_sql += """
                    ON CONFLICT ("sku_id", "real_date") DO UPDATE SET
                        "date" = EXCLUDED."date",
                        "brand" = EXCLUDED."brand",
                        "qty" = EXCLUDED."qty",
                        "per_ltr" = EXCLUDED."per_ltr",
                        "per_ltr_unit" = EXCLUDED."per_ltr_unit",
                        "uom" = EXCLUDED."uom",
                        "ltr_sold" = EXCLUDED."ltr_sold",
                        "month" = EXCLUDED."month",
                        "year" = EXCLUDED."year",
                        "item" = EXCLUDED."item",
                        "landing_rate" = EXCLUDED."landing_rate",
                        "basic_rate" = EXCLUDED."basic_rate",
                        "sale_amt_inclusive" = EXCLUDED."sale_amt_inclusive",
                        "sale_amt_exclusive" = EXCLUDED."sale_amt_exclusive",
                        "category" = EXCLUDED."category",
                        "sub_category" = EXCLUDED."sub_category",
                        "item_head" = EXCLUDED."item_head"
                """
            else:
                insert_sql += ' ON CONFLICT ("sku_id", "real_date") DO NOTHING'

            cur.executemany(insert_sql, rows)
            conn.commit()

        return {
            "success": len(rows),
            "failed": failed,
            "error": None,
            "missing_master": len(missing_master),
            "missing_price": len(missing_price),
            "table": "flipkart_grocery_master",
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        put_conn(conn)
