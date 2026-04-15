import httpx
from config import SUPABASE_URL, SUPABASE_KEY

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "count=exact",
}

REST_URL = f"{SUPABASE_URL}/rest/v1"


class SupabaseTable:
    """Lightweight Supabase REST wrapper using httpx."""

    def __init__(self, table: str):
        self.table = table
        self._params = {}
        self._headers = dict(HEADERS)

    def select(self, columns="*", count="exact"):
        self._params["select"] = columns
        if count:
            self._headers["Prefer"] = f"count={count}"
        return self

    def eq(self, col, val):
        self._params[col] = f"eq.{val}"
        return self

    def ilike(self, col, val):
        self._params[col] = f"ilike.{val}"
        return self

    def gte(self, col, val):
        self._params[col] = f"gte.{val}"
        return self

    def lte(self, col, val):
        self._params[col] = f"lte.{val}"
        return self

    def lt(self, col, val):
        self._params[col] = f"lt.{val}"
        return self

    def or_(self, clause):
        self._params["or"] = f"({clause})"
        return self

    def order(self, col, ascending=True):
        direction = "asc" if ascending else "desc"
        self._params["order"] = f"{col}.{direction}"
        return self

    def range(self, start, end):
        self._headers["Range"] = f"{start}-{end}"
        return self

    def limit(self, n):
        self._params["limit"] = str(n)
        return self

    def execute(self):
        url = f"{REST_URL}/{self.table}"
        resp = httpx.get(url, params=self._params, headers=self._headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Parse count from content-range header
        count = None
        cr = resp.headers.get("content-range", "")
        if "/" in cr:
            try:
                count = int(cr.split("/")[1])
            except (ValueError, IndexError):
                pass
        return _Result(data, count)


class _Result:
    def __init__(self, data, count):
        self.data = data
        self.count = count


class _Supabase:
    def table(self, name):
        return SupabaseTable(name)


supabase = _Supabase()
