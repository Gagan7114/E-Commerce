import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", 5432))
PG_DATABASE = os.getenv("PG_DATABASE", "ecom")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")

# JWT Auth
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production-use-a-long-random-string")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", 24))

# SAP HANA
SAP_HANA_HOST = os.getenv("SAP_HANA_HOST")
SAP_HANA_PORT = int(os.getenv("SAP_HANA_PORT", 30015))
SAP_HANA_USER = os.getenv("SAP_HANA_USER")
SAP_HANA_PASSWORD = os.getenv("SAP_HANA_PASSWORD")
SAP_HANA_DATABASE = os.getenv("SAP_HANA_DATABASE", "")
SAP_HANA_SCHEMA = os.getenv("SAP_HANA_SCHEMA", "")

# CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
