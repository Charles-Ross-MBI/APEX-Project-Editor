import streamlit as st

TAB_INSTRUCTIONS = {
    "Information": """
#### How to Use

This page displays a set of cards, each representing a specific section of data for the selected project.  
Each card shows the current values stored in AGOL, and you can edit those values directly inside the card.

---

**1. View and edit values inside each card**

Every card corresponds to a defined section of project data.  
When you expand a card, all fields for that section are immediately visible and editable.  
You can update any value directly in the card.

---

**2. Save your changes**

After making updates, press **UPDATE** at the bottom of the card.  
If the update to AGOL is successful, a **green checkmark** will appear next to the button.  
If the update fails, an **error message** will appear explaining the reason.

---

**3. Continue working across sections**

You may move between cards to review or update additional sections.  
To switch to another project, simply choose a different one from the dropdown.
"""
}






def instructions(section):
    """
    Display the unified instructions inside a Streamlit expander.
    """
    content = TAB_INSTRUCTIONS[section]
    with st.expander("Instructions", expanded=False):
        st.markdown(content)
