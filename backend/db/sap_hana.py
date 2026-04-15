from hdbcli import dbapi
from config import SAP_HANA_HOST, SAP_HANA_PORT, SAP_HANA_USER, SAP_HANA_PASSWORD, SAP_HANA_DATABASE, SAP_HANA_SCHEMA


def get_hana_connection():
    """Create a new SAP HANA DB connection."""
    kwargs = {
        "address": SAP_HANA_HOST,
        "port": SAP_HANA_PORT,
        "user": SAP_HANA_USER,
        "password": SAP_HANA_PASSWORD,
    }
    if SAP_HANA_DATABASE:
        kwargs["databaseName"] = SAP_HANA_DATABASE
    conn = dbapi.connect(**kwargs)
    if SAP_HANA_SCHEMA:
        conn.cursor().execute(f'SET SCHEMA "{SAP_HANA_SCHEMA}"')
    return conn


def query_hana(sql: str, params: tuple = None) -> list[dict]:
    """Execute a SELECT query and return rows as list of dicts."""
    conn = get_hana_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()
