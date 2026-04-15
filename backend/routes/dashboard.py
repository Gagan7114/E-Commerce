from fastapi import APIRouter, Query
from db.supabase_client import supabase

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# All tables the dashboard can query
ALLOWED_TABLES = [
    "master_po", "test_master_po",
    "amazon_sec_daily", "amazon_sec_range", "bigbasketSec", "blinkitSec",
    "fk_grocery_sec", "flipkartSec", "jiomartSec", "swiggySec", "zeptSec",
    "all_platform_inventory", "amazon_inventory", "bigbasket_inventory",
    "blinkit_inventory", "jiomart_inventory", "swiggy_inventory", "zepto_inventory",
    "truck_dispatches",
]


@router.get("/table-count/{table_name}")
async def get_table_count(table_name: str):
    if table_name not in ALLOWED_TABLES:
        return {"error": "Table not allowed", "count": 0}
    result = supabase.table(table_name).select("*", count="exact").limit(0).execute()
    return {"table": table_name, "count": result.count or 0}


@router.get("/table-counts")
async def get_all_table_counts():
    counts = {}
    for table in ALLOWED_TABLES:
        try:
            result = supabase.table(table).select("*", count="exact").limit(0).execute()
            counts[table] = result.count or 0
        except Exception:
            counts[table] = 0
    return counts


@router.get("/table-data/{table_name}")
async def get_table_data(
    table_name: str,
    page: int = Query(0, ge=0),
    page_size: int = Query(50, ge=1, le=200),
    search: str = Query("", max_length=200),
    search_columns: str = Query(""),  # comma separated
    date_column: str = Query(""),
    date_from: str = Query(""),
    date_to: str = Query(""),
    expiry_column: str = Query(""),
    expiry_before: str = Query(""),
):
    if table_name not in ALLOWED_TABLES:
        return {"error": "Table not allowed", "data": [], "count": 0}

    query = supabase.table(table_name).select("*", count="exact")

    # Date range filter
    if date_column and date_from:
        query = query.gte(date_column, date_from)
    if date_column and date_to:
        query = query.lte(date_column, date_to)

    # Expiry filter
    if expiry_column and expiry_before:
        query = query.lt(expiry_column, expiry_before)

    # Search filter
    if search and search_columns:
        cols = [c.strip() for c in search_columns.split(",") if c.strip()]
        or_clause = ",".join([f"{col}.ilike.%{search}%" for col in cols])
        if or_clause:
            query = query.or_(or_clause)

    # Pagination
    start = page * page_size
    query = query.range(start, start + page_size - 1)

    result = query.execute()
    return {
        "data": result.data or [],
        "count": result.count or 0,
        "page": page,
        "page_size": page_size,
    }
