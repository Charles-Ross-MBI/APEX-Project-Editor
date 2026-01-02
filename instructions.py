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
""",

    "AASHTOWare": """
#### How to Use

This tab displays the fields that are connected to the AASHTOWare database for this project.  
These values may be updated automatically when the live AASHTOWare connection is enabled.

---

**1. Control the live AASHTOWare connection**

At the top of this tab, you will find a toggle switch that controls the **live connection** to AASHTOWare.

- When **live updates are ON**, AASHTOWare will automatically push updates into the fields shown on this tab.  
- When **live updates are OFF**, automatic updates from AASHTOWare will stop, and the values will remain unchanged until manually edited.

---

**2. Manually update AASHTOWare-linked fields**

You may manually update any of the AASHTOWare-linked fields at any time.  
Simply make your changes in the card and press **UPDATE**.  
Your edits will be saved directly to AGOL for this project.

---

**3. Use AASHTOWare data alongside other project sections**

You can move between the AASHTOWare tab and other project sections at any time.  
Turning the live connection on or off does not affect your ability to edit other project data.
"""
}





def instructions(section):
    """
    Display the unified instructions inside a Streamlit expander.
    """
    content = TAB_INSTRUCTIONS[section]
    with st.expander("Instructions", expanded=False):
        st.markdown(content)
