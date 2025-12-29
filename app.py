import streamlit as st
from agol_util import get_multiple_fields

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
# Determine Current Project Label (if GUID exists)
# ---------------------------------------------------------
current_label = None
if st.session_state["guid"]:
    current_label = next(
        (label for label, gid in label_to_gid.items()
         if gid == st.session_state["guid"]),
        None
    )

# ---------------------------------------------------------
# Build RETURN Button HTML (always top-left)
# ---------------------------------------------------------
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
    <a href="{return_url}"
       onclick="window.top.location.replace('{return_url}'); return false;"
       style="display: inline-block;
              padding: 0.4rem 0.8rem;
              background-color: #e0e0e0;
              color: black;
              text-decoration: none;
              border-radius: 5px;
              font-weight: 600;">
        {return_button}
    </a>
    """,
    unsafe_allow_html=True
)



st.write("")  # small spacing under button

# ---------------------------------------------------------
# Project Selection or Project Name
# ---------------------------------------------------------
if not st.session_state["guid"]:
    # Title above dropdown
    #st.markdown("<h5>Select an APEX Project</h5>", unsafe_allow_html=True)

    # Dropdown
    selected_label = st.selectbox(
        "Select a project",
        labels_with_placeholder,
        index=0
    )

    # Update selection
    if selected_label != placeholder:
        st.session_state["guid"] = label_to_gid[selected_label]
        st.rerun()

    # Info message stays directly below the dropdown
    st.info("Select an APEX project to view and edit project information.")

else:
    # Project selected → show name under the return button
    if current_label:
        st.markdown(f"<h5>{current_label}</h5>", unsafe_allow_html=True)
    else:
        st.warning("Selected GUID not found in project list.")

# ---------------------------------------------------------
# Display Tabs When GUID Is Selected
# ---------------------------------------------------------
if st.session_state["guid"]:
    info, geom, geography, routes, comm, contacts, links = st.tabs([
        "INFORMATION",
        "GEOMETRY",
        "GEOGRAPHY",
        "ROUTES",
        "COMMUNITIES",
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
