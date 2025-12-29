import streamlit as st
from agol_util import get_multiple_fields

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(layout="wide")

# ---------------------------------------------------------
# Read URL Query Parameters
# ---------------------------------------------------------
params = st.query_params

guid_param = params.get("guid")
version_param = params.get("version")

# ---------------------------------------------------------
# Initialize Session State
# ---------------------------------------------------------
if "guid" not in st.session_state:
    st.session_state["guid"] = guid_param if guid_param else None

if "version" not in st.session_state:
    st.session_state["version"] = version_param if version_param else "edit"

# ---------------------------------------------------------
# Title Row (Title on left, RETURN button on right)
# ---------------------------------------------------------
col_title, col_return = st.columns([6, 1])

with col_title:
    st.title("APEX PROJECT EDITOR")

with col_return:
    version = st.session_state["version"]

    if version == "review":
        return_url = (
            "https://experience.arcgis.com/experience/"
            "e84a0f4117d1452396f407c080336f01/page/REVIEW-PROJECTS"
        )
        return_button = "RETURN TO REVIEW LIST"
    else:
        return_url = (
            "https://experience.arcgis.com/experience/"
            "e84a0f4117d1452396f407c080336f01"
        )
        return_button = "RETURN TO APEX"

    st.markdown(
        f"""
        <a href="{return_url}" target="_self"
           style="display: inline-block;
                  padding: 0.5rem 1rem;
                  background-color: #e0e0e0;
                  color: black;
                  text-decoration: none;
                  border-radius: 5px;
                  text-align: center;
                  font-weight: 600;
                  margin-top: 1.2rem;">
            {return_button}
        </a>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# Load Project List
# ---------------------------------------------------------
apex_url = (
    "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/"
    "service_0d036ae7c0a7424088ee565727d1bb66/FeatureServer"
)
fields = ["Proj_Name", "globalid"]

try:
    projects = get_multiple_fields(apex_url, 0, fields)
except Exception as e:
    st.error(f"Failed to load project list: {e}")
    projects = []

# Build mapping: Proj_Name → GlobalID
label_to_gid = {
    p.get("Proj_Name"): p.get("globalid")
    for p in projects
    if p.get("Proj_Name") and p.get("globalid")
}

labels = sorted(label_to_gid.keys())

placeholder = "— Select a project —"
labels_with_placeholder = [placeholder] + labels

# ---------------------------------------------------------
# Determine Dropdown Index (URL param takes priority)
# ---------------------------------------------------------
if st.session_state["guid"]:
    # Find label matching the GUID
    current_label = next(
        (label for label, gid in label_to_gid.items()
         if gid == st.session_state["guid"]),
        placeholder
    )
    index = labels_with_placeholder.index(current_label)
else:
    index = 0

# ---------------------------------------------------------
# Project Selection Dropdown
# ---------------------------------------------------------
selected_label = st.selectbox(
    "Select a Project",
    labels_with_placeholder,
    index=index
)

# Update session state when user selects a project
if selected_label == placeholder:
    st.session_state["guid"] = None
else:
    st.session_state["guid"] = label_to_gid[selected_label]

# ---------------------------------------------------------
# Display Tabs When GUID Is Selected
# ---------------------------------------------------------
if st.session_state["guid"]:
    info, geom, geography, routes, comm, contacts, links = st.tabs([
        "INFORMATION",
        "GEOMETRY",
        "GEOGRAPHY",
        "ROUTES",
        "IMPACTED COMMUNITIES",
        "CONTACTS",
        "WEB LINKS & ATTACHMENTS"
    ])

    with info:
        st.write("Content")

    with geom:
        st.write("Content")

    with geography:
        st.write("Content")

    with routes:
        st.write("Content")

    with comm:
        st.write("Content")

    with contacts:
        st.write("Content")

    with links:
        st.write("Content")

else:
    st.info("Select a Project to View and Edit Project Information")
