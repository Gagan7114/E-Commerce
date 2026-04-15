import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# SAP HANA
SAP_HANA_HOST = os.getenv("SAP_HANA_HOST")
SAP_HANA_PORT = int(os.getenv("SAP_HANA_PORT", 30015))
SAP_HANA_USER = os.getenv("SAP_HANA_USER")
SAP_HANA_PASSWORD = os.getenv("SAP_HANA_PASSWORD")
SAP_HANA_DATABASE = os.getenv("SAP_HANA_DATABASE", "")
SAP_HANA_SCHEMA = os.getenv("SAP_HANA_SCHEMA", "")

# CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
