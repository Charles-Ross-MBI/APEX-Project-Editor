import streamlit as st
from agol_util import select_record


def geometry_tab():

    record = select_record(url = st.session_state['projects_url'], 
                id_field = 'globalid', 
                id_value = st.session_state['guid'], 
                fields = "*", 
                return_geometry = True)


    st.markdown(record)