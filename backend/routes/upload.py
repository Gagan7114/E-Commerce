"""
Generic data upload endpoint for the uploader tool.
Supports batch INSERT and UPSERT (ON CONFLICT DO UPDATE).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from db.postgres_client import get_conn, put_conn

router = APIRouter(prefix="/api/upload", tags=["Upload"])

# Tables the uploader is allowed to write to
UPLOAD_ALLOWED_TABLES = [
    # Inventory
    "blinkit_inventory", "zepto_inventory", "swiggy_inventory",
    "bigbasket_inventory", "jiomart_inventory", "amazon_inventory",
    # Secondary sells
    "blinkitSec", "zeptoSec", "swiggySec", "flipkartSec",
    "jiomartSec", "bigbasketSec", "amazon_sec_daily", "amazon_sec_range",
    # Truck loading
    "blinkit_truck_loading",
]


class UploadRequest(BaseModel):
    table: str
    data: List[dict]
    unique_key: Optional[str] = None  # comma-separated conflict columns
    upsert: bool = True


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
