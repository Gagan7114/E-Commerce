"""
PostgreSQL database client — drop-in replacement for the old Supabase REST wrapper.
Uses psycopg2 with a connection pool for efficient access.
"""

import psycopg2
import psycopg2.pool
import psycopg2.extras
from config import PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD

# Connection pool (min 1, max 10 connections)
_pool = psycopg2.pool.ThreadedConnectionPool(
    1, 10,
    host=PG_HOST,
    port=PG_PORT,
    database=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
)


def get_conn():
    return _pool.getconn()


def put_conn(conn):
    _pool.putconn(conn)


class _Result:
    """Mimics the old Supabase result object with .data and .count."""
    def __init__(self, data, count):
        self.data = data
        self.count = count


class PostgresTable:
    """
    Chainable query builder that mirrors the old SupabaseTable API.
    Builds a SQL SELECT query with filters, ordering, pagination.
    """

    def __init__(self, table: str):
        self.table = table
        self._columns = "*"
        self._count = False
        self._filters = []       # list of (sql_fragment, params)
        self._or_clause = None   # raw OR clause
        self._order_col = None
        self._order_dir = "ASC"
        self._limit = None
        self._offset = None
        self._range_start = None
        self._range_end = None

    def select(self, columns="*", count=None):
        self._columns = columns
        if count == "exact":
            self._count = True
        return self

    def eq(self, col, val):
        self._filters.append((f'"{col}" = %s', [val]))
        return self

    def ilike(self, col, val):
        self._filters.append((f'"{col}" ILIKE %s', [val]))
        return self

    def gte(self, col, val):
        self._filters.append((f'"{col}" >= %s', [val]))
        return self

    def lte(self, col, val):
        self._filters.append((f'"{col}" <= %s', [val]))
        return self

    def lt(self, col, val):
        self._filters.append((f'"{col}" < %s', [val]))
        return self

    def or_(self, clause):
        """
        Accept a Supabase-style OR clause string like:
          "po_number.ilike.%search%,sku_name.ilike.%search%"
        and convert it to SQL.
        """
        self._or_clause = clause
        return self

    def order(self, col, ascending=True):
        self._order_col = col
        self._order_dir = "ASC" if ascending else "DESC"
        return self

    def range(self, start, end):
        self._range_start = start
        self._range_end = end
        return self

    def limit(self, n):
        self._limit = n
        return self

    def _parse_or_clause(self):
        """
        Parse Supabase-style or clause:
          "col.ilike.%val%,col2.ilike.%val2%"
        Returns (sql_fragment, params).
        """
        if not self._or_clause:
            return None, []

        parts = []
        params = []
        # Split by comma, but handle values that contain commas carefully
        raw = self._or_clause.strip("()")
        items = raw.split(",")

        for item in items:
            item = item.strip()
            if not item:
                continue
            # Format: col.operator.value
            segments = item.split(".", 2)
            if len(segments) < 3:
                continue
            col, op, val = segments[0], segments[1], segments[2]
            if op == "ilike":
                parts.append(f'"{col}" ILIKE %s')
                params.append(val)
            elif op == "eq":
                parts.append(f'"{col}" = %s')
                params.append(val)
            elif op == "gte":
                parts.append(f'"{col}" >= %s')
                params.append(val)
            elif op == "lte":
                parts.append(f'"{col}" <= %s')
                params.append(val)
            elif op == "lt":
                parts.append(f'"{col}" < %s')
                params.append(val)

        if parts:
            return "(" + " OR ".join(parts) + ")", params
        return None, []

    def execute(self):
        """Build and execute the SQL query, return _Result(data, count)."""
        conn = get_conn()
        try:
            # ── Build WHERE clause ──
            where_parts = []
            all_params = []

            for frag, prms in self._filters:
                where_parts.append(frag)
                all_params.extend(prms)

            or_sql, or_params = self._parse_or_clause()
            if or_sql:
                where_parts.append(or_sql)
                all_params.extend(or_params)

            where_sql = ""
            if where_parts:
                where_sql = " WHERE " + " AND ".join(where_parts)

            # ── Count query ──
            count = None
            if self._count:
                count_sql = f'SELECT COUNT(*) FROM "{self.table}"{where_sql}'
                with conn.cursor() as cur:
                    cur.execute(count_sql, all_params)
                    count = cur.fetchone()[0]

            # ── Data query ──
            cols = self._columns if self._columns != "*" else "*"
            if cols != "*":
                # Quote each column name
                col_list = ", ".join(f'"{c.strip()}"' for c in cols.split(","))
            else:
                col_list = "*"

            data_sql = f'SELECT {col_list} FROM "{self.table}"{where_sql}'

            if self._order_col:
                data_sql += f' ORDER BY "{self._order_col}" {self._order_dir}'

            # Pagination via range or limit
            data_params = list(all_params)
            if self._range_start is not None and self._range_end is not None:
                limit = self._range_end - self._range_start + 1
                data_sql += " LIMIT %s OFFSET %s"
                data_params.extend([limit, self._range_start])
            elif self._limit is not None:
                data_sql += " LIMIT %s"
                data_params.append(self._limit)

            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(data_sql, data_params)
                rows = cur.fetchall()

            # Convert RealDictRow to plain dicts and handle special types
            data = []
            for row in rows:
                d = dict(row)
                # Convert Decimal, date, datetime etc. to JSON-safe types
                for k, v in d.items():
                    if hasattr(v, 'isoformat'):
                        d[k] = v.isoformat()
                    elif isinstance(v, (bytes,)):
                        d[k] = v.decode('utf-8', errors='replace')
                    elif type(v).__name__ == 'Decimal':
                        d[k] = float(v)
                data.append(d)

            return _Result(data, count)
        finally:
            put_conn(conn)


class _Postgres:
    def table(self, name):
        return PostgresTable(name)


supabase = _Postgres()
