import streamlit as st
from init_session import init_session_state
from agol_util import get_multiple_fields, select_record
from information import information_tab
from geometry import geometry_tab
from instructions import instructions

# ---------------------------------------------------------
# Initialize Session State
# ---------------------------------------------------------
init_session_state()



# ---------------------------------------------------------
# Set Configuration
# --------------------------------------------------------- 
st.set_page_config(layout=st.session_state['mode'])




# ---------------------------------------------------------
# Read URL Query Parameters
# ---------------------------------------------------------
params = st.query_params

guid_param = params.get("guid")
version_param = params.get("version")

# Sync version
if version_param:
    st.session_state["version"] = version_param

# Sync GUID from URL into session_state
if guid_param and guid_param != st.session_state.get("guid"):
    st.session_state["guid"] = guid_param
    st.rerun()




# ---------------------------------------------------------
# Load Project List
# ---------------------------------------------------------
try:
    projects = get_multiple_fields(st.session_state['projects_url'], ["Proj_Name", "globalid"])
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
version = st.session_state.get("version")

if version == "review":
    return_button = "RETURN TO REVIEW LIST"
else:
    return_button = "RETURN TO APEX"

if version is not None:
    st.markdown(
        f"""
        <a href="#"
           onclick="window.top.history.back(); return false;"
           style="
               display: inline-block;
               padding: 0.4rem 0.8rem;
               background-color: #e0e0e0;
               color: black;
               text-decoration: none;
               border-radius: 5px;
               font-weight: 600;
           ">
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
    st.markdown("<h4>Select an APEX Project</h4>", unsafe_allow_html=True)

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
        st.markdown(f"<h3>{current_label}</h3>", unsafe_allow_html=True)
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
        st.write('')
        st.markdown("<h4>PROJECT INFORMATION 📄</h4>", unsafe_allow_html=True)
        st.write(
            "This page displays a set of project information cards that summarize key details for each project."
            "You can review, modify, and save project data as needed, updates will be written directly to the AGOL database."
        )
        instructions("Information")

        st.write("")
        st.write("")
        st.write("")
        information_tab()

    with geom:
        geometry_tab()

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
