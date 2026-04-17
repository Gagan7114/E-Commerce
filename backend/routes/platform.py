from fastapi import APIRouter, Query
from db.supabase_client import supabase

router = APIRouter(prefix="/api/platform", tags=["Platform"])

# Platform config (mirrors frontend config/platforms.js)
PLATFORMS = {
    "blinkit": {"inventory": "blinkit_inventory", "secondarySells": "blinkitSec", "masterPO": "master_po", "dispatches": "blinkit_truck_loading", "poFilterColumn": "format", "poFilterValue": "blinkit", "matchColumn": "item_id"},
    "zepto": {"inventory": "zepto_inventory", "secondarySells": "zeptoSec", "masterPO": "master_po", "dispatches": "truck_dispatches", "poFilterColumn": "format", "poFilterValue": "zepto", "matchColumn": "sku_code"},
    "jiomart": {"inventory": "jiomart_inventory", "secondarySells": "jiomartSec", "masterPO": "master_po", "dispatches": "truck_dispatches", "poFilterColumn": "format", "poFilterValue": "jiomart", "matchColumn": "sku_id"},
    "amazon": {"inventory": "amazon_inventory", "secondarySells": "amazon_sec_daily", "masterPO": "master_po", "dispatches": "truck_dispatches", "poFilterColumn": "format", "poFilterValue": "amazon", "matchColumn": "asin"},
    "bigbasket": {"inventory": "bigbasket_inventory", "secondarySells": "bigbasketSec", "masterPO": "master_po", "dispatches": "truck_dispatches", "poFilterColumn": "format", "poFilterValue": "big basket", "matchColumn": "sku_id"},
    "swiggy": {"inventory": "swiggy_inventory", "secondarySells": "swiggySec", "masterPO": "master_po", "dispatches": "truck_dispatches", "poFilterColumn": "format", "poFilterValue": "swiggy", "matchColumn": "sku_code"},
    "flipkart": {"inventory": "all_platform_inventory", "secondarySells": "flipkartSec", "masterPO": "master_po", "dispatches": "truck_dispatches", "poFilterColumn": "format", "poFilterValue": "flipkart", "matchColumn": "sku_code"},
}


def get_platform(slug: str):
    p = PLATFORMS.get(slug)
    if not p:
        raise ValueError(f"Unknown platform: {slug}")
    return p


@router.get("/{slug}/stats")
async def platform_stats(slug: str):
    p = get_platform(slug)
    filter_pattern = f"%{p['poFilterValue']}%"

    inv = supabase.table(p["inventory"]).select("*", count="exact").limit(0).execute()
    sells = supabase.table(p["secondarySells"]).select("*", count="exact").limit(0).execute()
    pos = supabase.table(p["masterPO"]).select("*", count="exact").ilike(p["poFilterColumn"], filter_pattern).limit(0).execute()

    return {
        "inventory": inv.count or 0,
        "sells": sells.count or 0,
        "openPOs": pos.count or 0,
        "activeTrucks": 0,
    }


@router.get("/{slug}/pos")
async def platform_pos(
    slug: str,
    page: int = Query(0, ge=0),
    page_size: int = Query(50, ge=1, le=200),
    search: str = Query(""),
):
    p = get_platform(slug)
    filter_pattern = f"%{p['poFilterValue']}%"

    query = supabase.table(p["masterPO"]).select("*", count="exact").ilike(p["poFilterColumn"], filter_pattern)

    if search:
        query = query.or_(
            f"po_number.ilike.%{search}%,"
            f"sku_name.ilike.%{search}%,"
            f"sku_code.ilike.%{search}%"
        )

    start = page * page_size
    result = query.range(start, start + page_size - 1).execute()

    return {
        "data": result.data or [],
        "count": result.count or 0,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{slug}/inventory-match")
async def inventory_match(slug: str, sku: str = Query(...)):
    p = get_platform(slug)
    result = supabase.table(p["inventory"]).select("*").eq(p["matchColumn"], sku).limit(1).execute()
    return {"match": result.data[0] if result.data else None}
