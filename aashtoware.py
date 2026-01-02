import streamlit as st
from datetime import datetime, date
import time
from agol_util import select_record, AGOLRecordLoader, AGOLDataLoader

# ---------------------------------------------------------
# Build and send an update payload to AGOL
# ---------------------------------------------------------
def update_section_to_agol(prefix, section, rows):
    attributes = {}

    for row in rows:
        for field in row:
            field_name = field["name"]
            key = f"{prefix}_{field_name}"
            attributes[field_name] = st.session_state.get(key, None)

    objectid_key = f"{prefix}_objectid"
    attributes["OBJECTID"] = st.session_state.get(objectid_key)

    payload = {"attributes": attributes}
    st.session_state[f"{section}_last_payload"] = payload

    loader = AGOLDataLoader(st.session_state["projects_url"])
    result = loader.update_features(payload)

    st.session_state[f"{section}_agol_result"] = result
    return result



# ---------------------------------------------------------
# Render a section (always edit mode)
# ---------------------------------------------------------
def render_section(section_name, data_prefix, widget_prefix, rows, on_save=None):

    # Always force edit mode
    edit_key = f"{widget_prefix}_edit_mode"
    st.session_state[edit_key] = True

    # Keys for success/error messages
    msg_key = f"{widget_prefix}_update_msg"
    msg_type_key = f"{widget_prefix}_update_type"
    msg_time_key = f"{widget_prefix}_update_time"

    with st.expander(f"**{section_name}**", expanded=True):

        # EDIT MODE ONLY
        for row in rows:
            cols = st.columns(len(row))
            for col, field in zip(cols, row):

                field_name = field["name"]
                label = field["label"]

                data_key = f"{data_prefix}_{field_name}"
                widget_key = f"{widget_prefix}_{field_name}"

                # Pull current value safely
                current_value = st.session_state.get(data_key, "")

                # Fix: ensure text_area receives a string, not None or NaN
                if current_value is None:
                    current_value = ""
                else:
                    current_value = str(current_value)

                field_type = field.get("type", "text")

                if field_type == "text":
                    col.text_input(label, value=current_value, key=widget_key)

                elif field_type == "text_area":
                    height = field.get("height", 150)
                    col.text_area(
                        label,
                        value=current_value,
                        height=height,
                        key=widget_key
                    )

                elif field_type == "select":
                    options = field.get("options", [])
                    col.selectbox(
                        label,
                        options,
                        index=options.index(current_value) if current_value in options else 0,
                        key=widget_key
                    )

                elif field_type == "number":
                    # Convert stored value into a usable number
                    try:
                        num_value = float(st.session_state.get(data_key)) \
                            if st.session_state.get(data_key) not in (None, "", "None") else 0.0
                    except:
                        num_value = 0.0

                    col.number_input(label, value=num_value, key=widget_key)


                elif field_type == "date":
                    raw = current_value

                    # Convert "2025-12-10" → datetime.date
                    if isinstance(raw, str) and raw.strip():
                        try:
                            raw = __import__("datetime").datetime.strptime(raw, "%Y-%m-%d").date()
                        except:
                            raw = None

                    # Convert epoch milliseconds → datetime.date
                    elif isinstance(raw, (int, float)):
                        try:
                            raw = __import__("datetime").datetime.utcfromtimestamp(raw / 1000).date()
                        except:
                            raw = None

                    # Ensure final value is a date or None
                    if not isinstance(raw, __import__("datetime").date):
                        raw = None

                    col.date_input(label, value=raw, key=widget_key)

                # Sync widget value back to real data key (SAFE VERSION)
                if widget_key in st.session_state:
                    st.session_state[data_key] = st.session_state[widget_key]

        # UPDATE BUTTON + MESSAGE
        col_btn, col_msg = st.columns([1, 6])

        with col_btn:
            if st.button("UPDATE", key=f"save_{widget_prefix}"):

                result = on_save(data_prefix, section_name.lower(), rows)

                # Correct success detection
                if isinstance(result, dict) and result.get("success") is True:
                    st.session_state[msg_key] = "success"
                    st.session_state[msg_type_key] = "success"
                else:
                    st.session_state[msg_key] = f"{result}"
                    st.session_state[msg_type_key] = "error"

                st.session_state[msg_time_key] = time.time()
                st.rerun()

        # DISPLAY MESSAGE + AUTO-HIDE
        with col_msg:
            msg_type = st.session_state.get(msg_type_key)
            msg = st.session_state.get(msg_key)
            msg_time = st.session_state.get(msg_time_key)

            if msg_type and msg_time:

                # Auto-hide after 3 seconds
                if time.time() - msg_time > 3:
                    st.session_state[msg_key] = None
                    st.session_state[msg_type_key] = None
                    st.session_state[msg_time_key] = None
                    st.rerun()

                # SUCCESS → green checkmark only
                if msg_type == "success":
                    st.markdown(
                        "<span style='font-size:24px; color:green;'>&#10004;</span>",
                        unsafe_allow_html=True
                    )

                # ERROR → show full error message
                elif msg_type == "error":
                    st.error(f"Update failed: {msg}")




def aashtoware_tab():

    # Load AGOL data only when not editing ANY information section
    if not any(k.endswith("aashtoware_edit_mode") and st.session_state[k] for k in st.session_state):
        AGOLRecordLoader(
            url=st.session_state["projects_url"],
            id_field="globalid",
            id_value=st.session_state["guid"],
            prefix="aashtoware",
            fields="*",
            return_geometry=False
        )

    live_updates = st.toggle("Live AASHTOWare Updates")

    # IDENTIFICATION
    aashtoware_rows = [
        [
            {"name": "iris", "label": "IRIS", "type": "text"},
        ],
        [
            {"name": "awp_proj_name", "label": "AASHTOWare Project Name", "type": "text"}
        ],
        [
            {"name": "fund_type", "label": "Funding Type", "type": "select",
             "options": st.session_state['funding']},
             {"name": "proj_prac", "label": "Practice", "type": "select",
             "options": st.session_state['practice']}
        ],
        [
            {"name": "award_date", "label": "Award Date", "type": "date"},
            {"name": "award_fiscal_year", "label": "Awarded Fiscal Year", "type": "select",
             "options": st.session_state['fiscal_year']}
        ],
        [
            {"name": "contractor", "label": "Awarded Contractor", "type": "text"},
        ],
        [
            {"name": "awarded_amount", "label": "Award Date", "type": "number"},
            {"name": "current_contract_amount", "label": "Current Contract Amount", "type": "number"},
            {"name": "amount_paid_to_date", "label": "Amount Paid to Date", "type": "number"},
        ],
        [
            {"name": "tenadd", "label": "Tenative Advertisd Date", "type": "date"},
        ]
    ]

    render_section(
        section_name="AASHTOWARE CONNECTED DATA",
        data_prefix="aashtoware",
        widget_prefix="aashtoware_identification",
        rows=aashtoware_rows,
        on_save=update_section_to_agol
    )
