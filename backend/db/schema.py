"""
Runtime schema bootstrap. Imported once at app startup to ensure
application-owned tables exist.
"""

from db.postgres_client import get_conn, put_conn


TRUCK_DISPATCHES_DDL = """
CREATE TABLE IF NOT EXISTS truck_dispatches (
    id               BIGSERIAL PRIMARY KEY,
    platform_slug    VARCHAR(32)  NOT NULL,
    platform         VARCHAR(64),
    mode             VARCHAR(16),
    truck_type       VARCHAR(32),
    capacity_kg      NUMERIC,
    loaded_kg        NUMERIC,
    fill_percentage  NUMERIC,
    po_count         INTEGER,
    po_details       JSONB,
    status           VARCHAR(32) DEFAULT 'dispatched',
    dispatch_date    DATE,
    dispatch_time    VARCHAR(8),
    vehicle_number   VARCHAR(32),
    driver_name      VARCHAR(100),
    driver_phone     VARCHAR(15),
    notes            TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_truck_dispatches_platform
    ON truck_dispatches (platform_slug, created_at DESC);
"""


USERS_ADMIN_DDL = """
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active    BOOLEAN DEFAULT TRUE;
"""


PERMISSIONS_DDL = """
CREATE TABLE IF NOT EXISTS permissions (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(64)  NOT NULL UNIQUE,
    description VARCHAR(200) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS groups (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(64)  NOT NULL UNIQUE,
    description VARCHAR(200) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS group_permissions (
    group_id      INTEGER NOT NULL REFERENCES groups(id)      ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (group_id, permission_id)
);

CREATE TABLE IF NOT EXISTS user_groups (
    user_id  INTEGER NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, group_id)
);

CREATE TABLE IF NOT EXISTS user_permissions (
    user_id       INTEGER NOT NULL REFERENCES users(id)        ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id)  ON DELETE CASCADE,
    PRIMARY KEY (user_id, permission_id)
);
"""


PLATFORM_CONFIG_DDL = """
CREATE TABLE IF NOT EXISTS platform_config (
    slug              VARCHAR(32) PRIMARY KEY,
    name              VARCHAR(64) NOT NULL,
    inventory_table   VARCHAR(64) NOT NULL,
    secondary_table   VARCHAR(64) NOT NULL,
    master_po_table   VARCHAR(64) NOT NULL DEFAULT 'master_po',
    po_filter_column  VARCHAR(64) NOT NULL DEFAULT 'format',
    po_filter_value   VARCHAR(64) NOT NULL,
    match_column      VARCHAR(64) NOT NULL,
    is_active         BOOLEAN     NOT NULL DEFAULT TRUE,
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


PLATFORM_SEED_DATA = [
    ("blinkit",   "Blinkit",   "blinkit_inventory",       "blinkitSec",       "blinkit",    "item_id"),
    ("zepto",     "Zepto",     "zepto_inventory",         "zeptoSec",         "zepto",      "sku_code"),
    ("jiomart",   "JioMart",   "jiomart_inventory",       "jiomartSec",       "jiomart",    "sku_id"),
    ("amazon",    "Amazon",    "amazon_inventory",        "amazon_sec_daily", "amazon",     "asin"),
    ("bigbasket", "BigBasket", "bigbasket_inventory",     "bigbasketSec",     "big basket", "sku_id"),
    ("swiggy",    "Swiggy",    "swiggy_inventory",        "swiggySec",        "swiggy",     "sku_code"),
    ("flipkart",  "Flipkart",  "all_platform_inventory",  "flipkartSec",      "flipkart",   "sku_code"),
]


def ensure_schema():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(TRUCK_DISPATCHES_DDL)
            cur.execute(USERS_ADMIN_DDL)
            cur.execute(PERMISSIONS_DDL)
            cur.execute(PLATFORM_CONFIG_DDL)

            # Seed platform_config if empty. Existing rows are preserved.
            cur.execute("SELECT COUNT(*) FROM platform_config")
            if cur.fetchone()[0] == 0:
                cur.executemany(
                    """
                    INSERT INTO platform_config
                        (slug, name, inventory_table, secondary_table,
                         po_filter_value, match_column)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (slug) DO NOTHING
                    """,
                    PLATFORM_SEED_DATA,
                )
        conn.commit()
    finally:
        put_conn(conn)
