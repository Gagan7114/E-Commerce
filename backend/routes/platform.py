import json
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Any, List, Optional
from db.postgres_client import db, get_conn, put_conn
from permissions import require_perm

router = APIRouter(prefix="/api/platform", tags=["Platform"])


# Platform config is stored in the `platform_config` table and managed via
# /admin. Cached in-process for CACHE_TTL seconds so admin edits show up
# shortly after save without requiring a restart.
CACHE_TTL = 30
_cache = {"data": None, "ts": 0.0}


def _load_platforms():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT slug, name, inventory_table, secondary_table, '
                'master_po_table, po_filter_column, po_filter_value, match_column '
                'FROM platform_config WHERE is_active = TRUE'
            )
            rows = cur.fetchall()
    finally:
        put_conn(conn)

    out = {}
    for slug, name, inv, sec, mpo, fcol, fval, mcol in rows:
        out[slug] = {
            "name": name,
            "inventory": inv,
            "secondarySells": sec,
            "masterPO": mpo,
            "dispatches": "truck_dispatches",
            "poFilterColumn": fcol,
            "poFilterValue": fval,
            "matchColumn": mcol,
        }
    return out


def _platforms():
    now = time.time()
    if _cache["data"] is None or (now - _cache["ts"]) > CACHE_TTL:
        _cache["data"] = _load_platforms()
        _cache["ts"] = now
    return _cache["data"]


def get_platform(slug: str):
    p = _platforms().get(slug)
    if not p:
        raise ValueError(f"Unknown platform: {slug}")
    return p


# Back-compat alias — some modules still import PLATFORMS directly.
def __getattr__(name):
    if name == "PLATFORMS":
        return _platforms()
    raise AttributeError(name)


@router.get("/{slug}/stats", dependencies=[Depends(require_perm("platform.stats.view"))])
async def platform_stats(slug: str):
    p = get_platform(slug)
    filter_pattern = f"%{p['poFilterValue']}%"

    inv = db.table(p["inventory"]).select("*", count="exact").limit(0).execute()
    sells = db.table(p["secondarySells"]).select("*", count="exact").limit(0).execute()
    pos = db.table(p["masterPO"]).select("*", count="exact").ilike(p["poFilterColumn"], filter_pattern).limit(0).execute()

    return {
        "inventory": inv.count or 0,
        "sells": sells.count or 0,
        "openPOs": pos.count or 0,
        "activeTrucks": 0,
    }


@router.get("/{slug}/pos", dependencies=[Depends(require_perm("platform.po.view"))])
async def platform_pos(
    slug: str,
    page: int = Query(0, ge=0),
    page_size: int = Query(50, ge=1, le=200),
    search: str = Query(""),
):
    p = get_platform(slug)
    filter_pattern = f"%{p['poFilterValue']}%"

    query = db.table(p["masterPO"]).select("*", count="exact").ilike(p["poFilterColumn"], filter_pattern)

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


@router.get("/{slug}/inventory-match", dependencies=[Depends(require_perm("platform.inventory.view"))])
async def inventory_match(slug: str, sku: str = Query(...)):
    p = get_platform(slug)
    result = db.table(p["inventory"]).select("*").eq(p["matchColumn"], sku).limit(1).execute()
    return {"match": result.data[0] if result.data else None}


# ─── Dispatches (truck_dispatches table) ──────────────────────────────

class DispatchCreate(BaseModel):
    platform: Optional[str] = None
    mode: Optional[str] = None
    truck_type: Optional[str] = None
    capacity_kg: Optional[float] = None
    loaded_kg: Optional[float] = None
    fill_percentage: Optional[float] = None
    po_count: Optional[int] = None
    po_details: Optional[List[Any]] = None
    status: Optional[str] = "dispatched"
    dispatch_date: Optional[str] = None
    dispatch_time: Optional[str] = None
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    notes: Optional[str] = None


@router.get("/{slug}/dispatches", dependencies=[Depends(require_perm("dispatch.view"))])
async def list_dispatches(slug: str):
    get_platform(slug)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, platform_slug, platform, mode, truck_type, capacity_kg, '
                'loaded_kg, fill_percentage, po_count, po_details, status, '
                'dispatch_date, dispatch_time, vehicle_number, driver_name, '
                'driver_phone, notes, created_at '
                'FROM truck_dispatches WHERE platform_slug = %s '
                'ORDER BY created_at DESC',
                [slug],
            )
            cols = [d[0] for d in cur.description]
            rows = []
            for row in cur.fetchall():
                d = dict(zip(cols, row))
                for k, v in list(d.items()):
                    if hasattr(v, "isoformat"):
                        d[k] = v.isoformat()
                    elif type(v).__name__ == "Decimal":
                        d[k] = float(v)
                rows.append(d)
            return {"data": rows, "count": len(rows)}
    finally:
        put_conn(conn)


@router.post("/{slug}/dispatches", dependencies=[Depends(require_perm("dispatch.add"))])
async def create_dispatch(slug: str, body: DispatchCreate):
    get_platform(slug)
    payload = body.model_dump()
    po_details = payload.pop("po_details", None)
    po_details_json = json.dumps(po_details) if po_details is not None else None

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO truck_dispatches '
                '(platform_slug, platform, mode, truck_type, capacity_kg, loaded_kg, '
                'fill_percentage, po_count, po_details, status, dispatch_date, '
                'dispatch_time, vehicle_number, driver_name, driver_phone, notes) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s) '
                'RETURNING id, created_at',
                [
                    slug,
                    payload["platform"],
                    payload["mode"],
                    payload["truck_type"],
                    payload["capacity_kg"],
                    payload["loaded_kg"],
                    payload["fill_percentage"],
                    payload["po_count"],
                    po_details_json,
                    payload["status"],
                    payload["dispatch_date"] or None,
                    payload["dispatch_time"],
                    payload["vehicle_number"],
                    payload["driver_name"],
                    payload["driver_phone"],
                    payload["notes"],
                ],
            )
            row = cur.fetchone()
            conn.commit()
            return {
                "id": row[0],
                "created_at": row[1].isoformat() if row[1] else None,
                "platform_slug": slug,
                "po_details": po_details,
                **{k: v for k, v in payload.items()},
            }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        put_conn(conn)


@router.delete("/{slug}/dispatches/{dispatch_id}", dependencies=[Depends(require_perm("dispatch.delete"))])
async def delete_dispatch(slug: str, dispatch_id: int):
    get_platform(slug)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'DELETE FROM truck_dispatches WHERE id = %s AND platform_slug = %s',
                [dispatch_id, slug],
            )
            deleted = cur.rowcount
            conn.commit()
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Dispatch not found")
        return {"deleted": deleted}
    finally:
        put_conn(conn)


@router.delete("/{slug}/dispatches", dependencies=[Depends(require_perm("dispatch.delete"))])
async def clear_dispatches(slug: str):
    get_platform(slug)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM truck_dispatches WHERE platform_slug = %s', [slug])
            deleted = cur.rowcount
            conn.commit()
        return {"deleted": deleted}
    finally:
        put_conn(conn)
