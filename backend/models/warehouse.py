"""
Warehouse tables — reflected from the existing schema so we don't hand-type
every column. These models are *read-only in admin* (populated by the external
uploader, not by us).
"""

from sqlalchemy import Column, Integer, MetaData, Table

from db.sqlalchemy_db import Base, engine


# Tables the admin should browse. Reflected at import time.
_WAREHOUSE_TABLES = [
    "master_po",
    "test_master_po",
    "blinkit_inventory",
    "zepto_inventory",
    "swiggy_inventory",
    "bigbasket_inventory",
    "jiomart_inventory",
    "amazon_inventory",
    "all_platform_inventory",
    "blinkitSec",
    "zeptoSec",
    "swiggySec",
    "bigbasketSec",
    "flipkartSec",
    "jiomartSec",
    "amazon_sec_daily",
    "amazon_sec_range",
    "flipkart_grocery_master",
    "fk_grocery",
    "blinkit_truck_loading",
]


def _reflect_model(class_name, table_name):
    """Reflect a table into a SQLAlchemy declarative model at runtime."""
    metadata = MetaData()
    try:
        tbl = Table(table_name, metadata, autoload_with=engine)
    except Exception as e:
        print(f"[warehouse] could not reflect {table_name}: {e}")
        return None

    # SQLAlchemy ORM mapping requires a primary key. If the real table has
    # none, use the first column as an ORM-level synthetic PK (no schema
    # change — just tells the mapper which column identifies a row).
    pk_cols = list(tbl.primary_key.columns)
    if not pk_cols:
        pk_cols = [next(iter(tbl.columns))]

    first_col_name = next(iter(tbl.columns)).name

    return type(
        class_name,
        (Base,),
        {
            "__table__": tbl,
            "__mapper_args__": {"primary_key": pk_cols},
            "__str__": lambda self: f"{table_name} #{getattr(self, first_col_name, '?')}",
        },
    )


WAREHOUSE_MODELS = {}
for _t in _WAREHOUSE_TABLES:
    # camel-case model name: blinkit_inventory -> BlinkitInventory, blinkitSec -> BlinkitSec
    parts = _t.replace("Sec", "_sec").split("_")
    cls_name = "".join(p.capitalize() for p in parts if p)
    model = _reflect_model(cls_name, _t)
    if model is not None:
        WAREHOUSE_MODELS[_t] = model
