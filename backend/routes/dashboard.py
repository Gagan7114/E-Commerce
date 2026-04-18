from fastapi import APIRouter, Query
from db.postgres_client import db
from collections import defaultdict

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# All tables the dashboard can query
ALLOWED_TABLES = [
    "master_po", "test_master_po",
    "amazon_sec_daily", "amazon_sec_range", "bigbasketSec", "blinkitSec",
    "fk_grocery", "flipkartSec", "jiomartSec", "swiggySec", "zeptoSec",
    "amazon_inventory", "bigbasket_inventory",
    "blinkit_inventory", "jiomart_inventory", "swiggy_inventory", "zepto_inventory",
    "all_platform_inventory",
    "blinkit_truck_loading",
]


@router.get("/table-count/{table_name}")
async def get_table_count(table_name: str):
    if table_name not in ALLOWED_TABLES:
        return {"error": "Table not allowed", "count": 0}
    result = db.table(table_name).select("*", count="exact").limit(0).execute()
    return {"table": table_name, "count": result.count or 0}


@router.get("/table-counts")
async def get_all_table_counts():
    counts = {}
    for table in ALLOWED_TABLES:
        try:
            result = db.table(table).select("*", count="exact").limit(0).execute()
            counts[table] = result.count or 0
        except Exception:
            counts[table] = 0
    return counts


INVENTORY_CONFIG = {
    "blinkit": {"table": "blinkit_inventory", "qty_col": "total_inv_qty", "name_col": "item_name", "city_col": None, "color": "#f5c518"},
    "zepto": {"table": "zepto_inventory", "qty_col": "units", "name_col": "sku_name", "city_col": "city", "color": "#7b2ff7"},
    "swiggy": {"table": "swiggy_inventory", "qty_col": "warehouse_qty_available", "name_col": "sku_description", "city_col": "city", "color": "#fc8019"},
    "bigbasket": {"table": "bigbasket_inventory", "qty_col": "soh", "name_col": "sku_name", "city_col": "city", "color": "#84c225"},
    "jiomart": {"table": "jiomart_inventory", "qty_col": "total_sellable_inv", "name_col": "title", "city_col": None, "color": "#0078ad"},
    "amazon": {"table": "amazon_inventory", "qty_col": "sellable_on_hand_units", "name_col": "product_title", "id_col": "asin", "city_col": None, "color": "#ff9900"},
}


def _is_code(name: str) -> bool:
    """Check if a name looks like an ID/ASIN/code rather than a real product name."""
    if not name:
        return True
    name = name.strip()
    if len(name) <= 12 and name.isalnum():
        return True
    return False


@router.get("/inventory-charts")
async def inventory_charts():
    """Aggregate inventory data across all platforms for dashboard charts."""
    platform_totals = []
    city_totals = defaultdict(int)
    top_products = []

    for platform, cfg in INVENTORY_CONFIG.items():
        table = cfg["table"]
        qty_col = cfg["qty_col"]
        name_col = cfg["name_col"]
        id_col = cfg.get("id_col")
        city_col = cfg["city_col"]

        try:
            # Get all rows with only needed columns for aggregation
            select_cols = [qty_col, name_col]
            if id_col:
                select_cols.append(id_col)
            if city_col:
                select_cols.append(city_col)
            cols_str = ",".join(select_cols)

            result = db.table(table).select(cols_str, count="exact").limit(5000).execute()
            rows = result.data or []
            total_count = result.count or 0

            # For Amazon: build ASIN → real product name lookup from rows that have proper names
            name_lookup = {}
            if id_col:
                for r in rows:
                    rid = r.get(id_col)
                    rname = r.get(name_col)
                    if rid and rname and not _is_code(rname):
                        name_lookup[rid] = rname

            # Platform total stock
            total_qty = sum(int(r.get(qty_col) or 0) for r in rows)
            platform_totals.append({
                "platform": platform,
                "total_qty": total_qty,
                "sku_count": total_count,
                "color": cfg["color"],
            })

            # City-wise aggregation
            if city_col:
                for r in rows:
                    city = r.get(city_col)
                    qty = int(r.get(qty_col) or 0)
                    if city and qty > 0:
                        city_totals[city.upper().strip()] += qty

            # Top products per platform (aggregate by product name)
            product_map = defaultdict(int)
            for r in rows:
                name = r.get(name_col)
                qty = int(r.get(qty_col) or 0)
                if not name or qty <= 0:
                    continue
                # If name looks like a code, try to resolve it via lookup
                if _is_code(name) and id_col:
                    rid = r.get(id_col) or name
                    name = name_lookup.get(rid, name)
                product_map[name] += qty

            for name, qty in sorted(product_map.items(), key=lambda x: -x[1])[:5]:
                top_products.append({
                    "product": name[:80],
                    "qty": qty,
                    "platform": platform,
                    "color": cfg["color"],
                })

        except Exception:
            platform_totals.append({
                "platform": platform,
                "total_qty": 0,
                "sku_count": 0,
                "color": cfg["color"],
            })

    # Sort results
    platform_totals.sort(key=lambda x: -x["total_qty"])

    city_list = [{"city": city, "qty": qty} for city, qty in city_totals.items()]
    city_list.sort(key=lambda x: -x["qty"])

    top_products.sort(key=lambda x: -x["qty"])

    return {
        "platform_totals": platform_totals,
        "city_distribution": city_list[:15],
        "top_products": top_products[:15],
    }


@router.get("/table-columns/{table_name}")
async def get_table_columns(table_name: str):
    """Return column names and a sample row for a table (for frontend column detection)."""
    if table_name not in ALLOWED_TABLES:
        return {"error": "Table not allowed", "columns": [], "sample": None}
    try:
        result = db.table(table_name).select("*").range(0, 0).execute()
        if result.data and len(result.data) > 0:
            return {"columns": list(result.data[0].keys()), "sample": result.data[0]}
        return {"columns": [], "sample": None}
    except Exception:
        return {"columns": [], "sample": None}


@router.get("/expiry-alerts/{table_name}")
async def get_expiry_alerts(table_name: str):
    """Scan a table for expired / expiring-soon rows based on date columns."""
    import re
    from datetime import date, timedelta

    if table_name not in ALLOWED_TABLES:
        return {"alerts": []}

    DATE_COL_PATTERNS = re.compile(
        r"expir|delivery_date|deliver_by|due_date|valid_until|best_before|shelf_life|end_date|dispatch_date", re.I
    )
    ALERT_DAYS = 7

    try:
        # Get a sample row to detect date columns
        sample_result = db.table(table_name).select("*").range(0, 0).execute()
        if not sample_result.data or len(sample_result.data) == 0:
            return {"alerts": []}

        sample = sample_result.data[0]
        cols = list(sample.keys())
        date_cols = [
            c for c in cols
            if DATE_COL_PATTERNS.search(c)
            and sample.get(c)
            and isinstance(sample[c], str)
            and re.match(r"^\d{4}-\d{2}-\d{2}", sample[c])
        ]
        if not date_cols:
            return {"alerts": []}

        today = date.today()
        soon = today + timedelta(days=ALERT_DAYS)
        today_str = today.isoformat()
        soon_str = soon.isoformat()

        alerts = []
        for col in date_cols:
            # Expired
            expired_result = (
                db.table(table_name)
                .select("*", count="exact")
                .lt(col, today_str)
                .range(0, 4)
                .execute()
            )
            if expired_result.count and expired_result.count > 0:
                alerts.append({
                    "table": table_name,
                    "column": col,
                    "type": "expired",
                    "count": expired_result.count,
                    "rows": expired_result.data or [],
                })

            # Expiring soon
            expiring_result = (
                db.table(table_name)
                .select("*", count="exact")
                .gte(col, today_str)
                .lte(col, soon_str)
                .range(0, 4)
                .execute()
            )
            if expiring_result.count and expiring_result.count > 0:
                alerts.append({
                    "table": table_name,
                    "column": col,
                    "type": "expiring",
                    "count": expiring_result.count,
                    "rows": expiring_result.data or [],
                })

        return {"alerts": alerts}
    except Exception:
        return {"alerts": []}


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
    year: str = Query(""),
    month: str = Query(""),
    date: str = Query(""),
    expiry_column: str = Query(""),
    expiry_before: str = Query(""),
):
    if table_name not in ALLOWED_TABLES:
        return {"error": "Table not allowed", "data": [], "count": 0}

    query = db.table(table_name).select("*", count="exact")

    # Date range filter (direct from/to)
    if date_column and date_from:
        query = query.gte(date_column, date_from)
    if date_column and date_to:
        query = query.lte(date_column, date_to)

    # Year / month / date filters (used by frontend buildQuery)
    if date_column and year and not date_from and not date_to:
        query = query.gte(date_column, f"{year}-01-01")
        query = query.lte(date_column, f"{year}-12-31T23:59:59")
    if date_column and month:
        import calendar
        y = year or str(__import__('datetime').datetime.now().year)
        m = str(month).zfill(2)
        last_day = calendar.monthrange(int(y), int(month))[1]
        query = query.gte(date_column, f"{y}-{m}-01")
        query = query.lte(date_column, f"{y}-{m}-{last_day}T23:59:59")
    if date_column and date and not date_from and not date_to:
        query = query.gte(date_column, date)
        query = query.lte(date_column, f"{date}T23:59:59")

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
