import os
import streamlit as st
from dotenv import load_dotenv


def init_session_state():
    """Initialize all session state values."""

    # ---------------------------------------------------------
    # DEFAULTS
    # ---------------------------------------------------------
    defaults = {
        "user_logged_in": False,
        "theme": "light",
        "mode": 'centered',
        "counter": 0,
        "data_loaded": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


    # ---------------------------------------------------------
    # VALUES
    # ---------------------------------------------------------

    value_lists = {
        'construction_years': ["CY2025", "CY2026", "CY2027", "CY2028", "CY2029", "CY2030"],
        'phase': ["Planning", "Construction"],
        'funding': ["FHWY", "FHWA", "FAA", "STATE", "OTHER"],
        'practice': ['Highways', "Aviation", "Facilities", "Marine Highway", "Other"]
    }
    for key, value in value_lists.items():
        st.session_state.setdefault(key, value)


    # ---------------------------------------------------------
    # URL PARAMETERS
    # ---------------------------------------------------------
    url_params = {
        "guid": None,
        "version": None
    }
    for key, value in url_params.items():
        st.session_state.setdefault(key, value)



    # ---------------------------------------------------------
    # APEX URLS
    # ---------------------------------------------------------
    apex_urls = {
        "projects_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer/0",
        "sites_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer/1",
        "routes_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer/2",
        "impact_comms_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer/3",
        "region_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer/4",
        "bor_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer/5",
        "senate_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer/6",
        "house_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer/7",
        "impact_routes_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer/8",
        "contacts_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer/9",
        "aashtoware_url": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/AWP_PROJECTS_EXPORT_XYTableToPoint_ExportFeatures/FeatureServer/0",
        "mileposts": "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/AKDOT_Routes_Mileposts/FeatureServer/0"
    }
    for key, value in apex_urls.items():
        st.session_state.setdefault(key, value)



    # ---------------------------------------------------------
    # AGOL CREDENTIALS
    # ---------------------------------------------------------

    # 1. Check if a .env file exists
    env_file_exists = os.path.exists(".env")

    env_user = None
    env_pass = None

    if env_file_exists:
        load_dotenv()
        agol_username = os.getenv("AGOL_USERNAME")
        agol_password = os.getenv("AGOL_PASSWORD")

    else:
        # 2. Check secrets (may or may not exist)
        agol_username = st.secrets.get("AGOL_USERNAME") if hasattr(st, "secrets") else None
        agol_password = st.secrets.get("AGOL_PASSWORD") if hasattr(st, "secrets") else None


    # 4. Store in session_state safely
    st.session_state.setdefault("AGOL_USERNAME", agol_username)
    st.session_state.setdefault("AGOL_PASSWORD", agol_password)



# --------------------------------------------------------- 
# RUN AUTOMATICALLY WHEN IMPORTED 
# --------------------------------------------------------- 
init_session_state()
