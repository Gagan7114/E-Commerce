from fastapi import APIRouter, Query, HTTPException
from db.sap_hana import query_hana

router = APIRouter(prefix="/api/sap", tags=["SAP B1"])

# Platform slug → SAP U_Chain values + CardName patterns
PLATFORM_CHAIN_MAP = {
    "blinkit": {"chains": [], "names": ["%blinkit%", "%blink commerce%", "%fashnear%", "%grofer%"]},
    "zepto": {"chains": [], "names": ["%zepto%", "%kiranakart%"]},
    "jiomart": {"chains": ["JIOMART"], "names": ["%jiomart%", "%reliance retail%"]},
    "amazon": {"chains": ["AMAZON"], "names": ["%amazon%"]},
    "bigbasket": {"chains": ["BIG BASKET"], "names": ["%bigbasket%", "%big basket%", "%innovative retail%"]},
    "swiggy": {"chains": ["SWIGGY"], "names": ["%swiggy%", "%scootsy%"]},
    "flipkart": {"chains": ["FLIPKART"], "names": ["%flipkart%"]},
}


@router.get("/distributors")
async def get_distributors(
    search: str = Query(""),
    page: int = Query(0, ge=0),
    page_size: int = Query(50, ge=1, le=200),
):
    """Fetch all distributors (Business Partners of type Supplier) from SAP B1."""
    offset = page * page_size

    where = "WHERE T0.\"CardType\" = 'S'"
    params = ()

    if search:
        where += (
            " AND (T0.\"CardCode\" LIKE ? OR T0.\"CardName\" LIKE ?"
            " OR T0.\"Phone1\" LIKE ? OR T0.\"City\" LIKE ?)"
        )
        s = f"%{search}%"
        params = (s, s, s, s)

    sql = f"""
        SELECT
            T0."CardCode",
            T0."CardName",
            T0."CardType",
            T0."GroupCode",
            T0."Phone1",
            T0."Phone2",
            T0."Cellular",
            T0."Fax",
            T0."E_Mail" AS "Email",
            T0."Address",
            T0."City",
            T0."ZipCode",
            T0."State1" AS "State",
            T0."Country",
            T0."Currency",
            T0."Balance",
            T0."CreditLine",
            T0."LicTradNum" AS "GSTIN",
            T0."validFor" AS "Active",
            T0."CreateDate",
            T0."UpdateDate"
        FROM OCRD T0
        {where}
        ORDER BY T0."CardName"
        LIMIT {page_size} OFFSET {offset}
    """
    try:
        data = query_hana(sql, params if params else None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAP HANA error: {str(e)}")

    count_sql = f'SELECT COUNT(*) AS "total" FROM OCRD T0 {where}'
    try:
        count_result = query_hana(count_sql, params if params else None)
        total = count_result[0]["total"] if count_result else 0
    except Exception:
        total = len(data)

    return {"data": data, "count": total, "page": page, "page_size": page_size}


@router.get("/distributors/{card_code}")
async def get_distributor_detail(card_code: str):
    """Fetch a single distributor by CardCode with addresses and contacts."""
    bp_sql = """
        SELECT
            T0."CardCode", T0."CardName", T0."CardType", T0."GroupCode",
            T0."Phone1", T0."Phone2", T0."Cellular", T0."Fax",
            T0."E_Mail" AS "Email",
            T0."Address", T0."City", T0."ZipCode", T0."State1" AS "State",
            T0."Country", T0."Currency", T0."Balance", T0."CreditLine",
            T0."LicTradNum" AS "GSTIN", T0."validFor" AS "Active",
            T0."CreateDate", T0."UpdateDate"
        FROM OCRD T0
        WHERE T0."CardCode" = ?
    """
    addr_sql = """
        SELECT
            T0."Address", T0."AdresType", T0."Street", T0."Block",
            T0."City", T0."ZipCode", T0."State", T0."Country"
        FROM CRD1 T0
        WHERE T0."CardCode" = ?
    """
    contact_sql = """
        SELECT
            T0."Name", T0."FirstName", T0."LastName",
            T0."Tel1", T0."Tel2", T0."E_MailL" AS "Email",
            T0."Position", T0."Active"
        FROM OCPR T0
        WHERE T0."CardCode" = ?
    """
    try:
        bp = query_hana(bp_sql, (card_code,))
        addresses = query_hana(addr_sql, (card_code,))
        contacts = query_hana(contact_sql, (card_code,))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAP HANA error: {str(e)}")

    if not bp:
        raise HTTPException(status_code=404, detail="Distributor not found")

    return {"distributor": bp[0], "addresses": addresses, "contacts": contacts}


@router.get("/distributor-orders/{card_code}")
async def get_distributor_orders(
    card_code: str,
    page: int = Query(0, ge=0),
    page_size: int = Query(50, ge=1, le=200),
):
    """Fetch purchase orders from a specific distributor."""
    offset = page * page_size
    sql = f"""
        SELECT
            T0."DocEntry", T0."DocNum", T0."DocDate", T0."DocDueDate",
            T0."CardCode", T0."CardName", T0."DocTotal", T0."DocCur",
            T0."DocStatus", T0."NumAtCard" AS "VendorRef",
            T0."Comments"
        FROM OPOR T0
        WHERE T0."CardCode" = ?
        ORDER BY T0."DocDate" DESC
        LIMIT {page_size} OFFSET {offset}
    """
    count_sql = 'SELECT COUNT(*) AS "total" FROM OPOR T0 WHERE T0."CardCode" = ?'

    try:
        data = query_hana(sql, (card_code,))
        count_result = query_hana(count_sql, (card_code,))
        total = count_result[0]["total"] if count_result else 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAP HANA error: {str(e)}")

    return {"data": data, "count": total, "page": page, "page_size": page_size}


@router.get("/distributor-invoices/{card_code}")
async def get_distributor_invoices(
    card_code: str,
    page: int = Query(0, ge=0),
    page_size: int = Query(50, ge=1, le=200),
):
    """Fetch AP invoices from a specific distributor."""
    offset = page * page_size
    sql = f"""
        SELECT
            T0."DocEntry", T0."DocNum", T0."DocDate", T0."DocDueDate",
            T0."CardCode", T0."CardName", T0."DocTotal", T0."DocCur",
            T0."DocStatus", T0."NumAtCard" AS "VendorRef",
            T0."Comments"
        FROM OPCH T0
        WHERE T0."CardCode" = ?
        ORDER BY T0."DocDate" DESC
        LIMIT {page_size} OFFSET {offset}
    """
    count_sql = 'SELECT COUNT(*) AS "total" FROM OPCH T0 WHERE T0."CardCode" = ?'

    try:
        data = query_hana(sql, (card_code,))
        count_result = query_hana(count_sql, (card_code,))
        total = count_result[0]["total"] if count_result else 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAP HANA error: {str(e)}")

    return {"data": data, "count": total, "page": page, "page_size": page_size}


@router.get("/items")
async def get_items(
    search: str = Query(""),
    page: int = Query(0, ge=0),
    page_size: int = Query(50, ge=1, le=200),
):
    """Fetch items/products from SAP B1 item master."""
    offset = page * page_size

    where = "WHERE 1=1"
    params = ()

    if search:
        where += (
            " AND (T0.\"ItemCode\" LIKE ? OR T0.\"ItemName\" LIKE ?"
            " OR T0.\"CodeBars\" LIKE ?)"
        )
        s = f"%{search}%"
        params = (s, s, s)

    sql = f"""
        SELECT
            T0."ItemCode", T0."ItemName", T0."CodeBars" AS "Barcode",
            T0."ItmsGrpCod" AS "GroupCode",
            T0."OnHand" AS "InStock", T0."IsCommited" AS "Committed",
            T0."OnOrder", T0."Available",
            T0."BuyUnitMsr" AS "PurchaseUOM", T0."SalUnitMsr" AS "SalesUOM",
            T0."LastPurPrc" AS "LastPurchasePrice",
            T0."LastPurCur" AS "Currency",
            T0."validFor" AS "Active"
        FROM OITM T0
        {where}
        ORDER BY T0."ItemName"
        LIMIT {page_size} OFFSET {offset}
    """
    count_sql = f'SELECT COUNT(*) AS "total" FROM OITM T0 {where}'

    try:
        data = query_hana(sql, params if params else None)
        count_result = query_hana(count_sql, params if params else None)
        total = count_result[0]["total"] if count_result else 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAP HANA error: {str(e)}")

    return {"data": data, "count": total, "page": page, "page_size": page_size}


@router.get("/stock-by-warehouse")
async def get_stock_by_warehouse(
    item_code: str = Query(""),
):
    """Fetch warehouse-wise stock for an item."""
    where = 'WHERE T0."OnHand" > 0'
    params = ()

    if item_code:
        where += ' AND T0."ItemCode" = ?'
        params = (item_code,)

    sql = f"""
        SELECT
            T0."ItemCode", T1."ItemName",
            T0."WhsCode", T0."OnHand", T0."IsCommited" AS "Committed",
            T0."OnOrder", T0."OnHand" - T0."IsCommited" AS "Available"
        FROM OITW T0
        INNER JOIN OITM T1 ON T0."ItemCode" = T1."ItemCode"
        {where}
        ORDER BY T0."WhsCode"
    """
    try:
        data = query_hana(sql, params if params else None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAP HANA error: {str(e)}")

    return {"data": data}


def _build_platform_where(slug: str) -> tuple[str, tuple]:
    """Build WHERE clause to filter BPs by platform."""
    mapping = PLATFORM_CHAIN_MAP.get(slug)
    if not mapping:
        raise HTTPException(status_code=404, detail=f"Unknown platform: {slug}")

    conditions = []
    params = []

    for chain in mapping["chains"]:
        conditions.append('T0."U_Chain" = ?')
        params.append(chain)

    for pattern in mapping["names"]:
        conditions.append('LOWER(T0."CardName") LIKE ?')
        params.append(pattern)

    where = f"({' OR '.join(conditions)})" if conditions else "1=0"
    return where, tuple(params)


@router.get("/platform-distributors/{slug}")
async def get_platform_distributors(
    slug: str,
    search: str = Query(""),
    page: int = Query(0, ge=0),
    page_size: int = Query(50, ge=1, le=200),
):
    """Fetch distributors (both customers & vendors) linked to a specific platform."""
    platform_where, platform_params = _build_platform_where(slug)

    search_clause = ""
    search_params = ()
    if search:
        search_clause = (
            " AND (T0.\"CardCode\" LIKE ? OR T0.\"CardName\" LIKE ?"
            " OR T0.\"Phone1\" LIKE ? OR T0.\"City\" LIKE ?)"
        )
        s = f"%{search}%"
        search_params = (s, s, s, s)

    where = f"WHERE {platform_where}{search_clause}"
    all_params = platform_params + search_params

    offset = page * page_size
    sql = f"""
        SELECT
            T0."CardCode", T0."CardName", T0."CardType",
            T0."U_Chain" AS "Chain", T0."U_Main_Group" AS "MainGroup",
            T0."Phone1", T0."Cellular",
            T0."E_Mail" AS "Email",
            T0."Address", T0."City", T0."State1" AS "State",
            T0."Country", T0."Currency", T0."Balance", T0."CreditLine",
            T0."LicTradNum" AS "GSTIN",
            T0."validFor" AS "Active",
            T0."CreateDate", T0."UpdateDate"
        FROM OCRD T0
        {where}
        ORDER BY T0."CardName"
        LIMIT {page_size} OFFSET {offset}
    """
    count_sql = f'SELECT COUNT(*) AS "total" FROM OCRD T0 {where}'

    try:
        data = query_hana(sql, all_params if all_params else None)
        count_result = query_hana(count_sql, all_params if all_params else None)
        total = count_result[0]["total"] if count_result else 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAP HANA error: {str(e)}")

    return {"data": data, "count": total, "page": page, "page_size": page_size}


@router.get("/platform-distributors/{slug}/{card_code}")
async def get_platform_distributor_detail(slug: str, card_code: str):
    """Fetch a single distributor detail within platform context."""
    bp_sql = """
        SELECT
            T0."CardCode", T0."CardName", T0."CardType",
            T0."U_Chain" AS "Chain", T0."U_Main_Group" AS "MainGroup",
            T0."Phone1", T0."Phone2", T0."Cellular", T0."Fax",
            T0."E_Mail" AS "Email",
            T0."Address", T0."City", T0."ZipCode", T0."State1" AS "State",
            T0."Country", T0."Currency", T0."Balance", T0."CreditLine",
            T0."LicTradNum" AS "GSTIN", T0."validFor" AS "Active",
            T0."CreateDate", T0."UpdateDate"
        FROM OCRD T0
        WHERE T0."CardCode" = ?
    """
    addr_sql = """
        SELECT T0."Address", T0."AdresType", T0."Street", T0."Block",
               T0."City", T0."ZipCode", T0."State", T0."Country"
        FROM CRD1 T0 WHERE T0."CardCode" = ?
    """
    contact_sql = """
        SELECT T0."Name", T0."FirstName", T0."LastName",
               T0."Tel1", T0."Tel2", T0."E_MailL" AS "Email",
               T0."Position", T0."Active"
        FROM OCPR T0 WHERE T0."CardCode" = ?
    """
    try:
        bp = query_hana(bp_sql, (card_code,))
        addresses = query_hana(addr_sql, (card_code,))
        contacts = query_hana(contact_sql, (card_code,))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAP HANA error: {str(e)}")

    if not bp:
        raise HTTPException(status_code=404, detail="Distributor not found")

    return {"distributor": bp[0], "addresses": addresses, "contacts": contacts}
