import streamlit as st

TAB_INSTRUCTIONS = {
    "APEX Instructions": """
### How to Use the APEX Project Editor

#### 1. Select a Project
Use the **dropdown list at the top of the page** to select an APEX project.  
The list contains all available projects from the APEX database.

- If no project is selected, the editor will remain inactive.
- Once a project is selected, the full set of tabs will appear.

---

#### 2. Navigate Through the Tabs
After selecting a project, you will see several tabs such as:

- **INFORMATION**  
- **GEOMETRY**  
- **GEOGRAPHY**  
- **ROUTES**  
- **IMPACTED COMMUNITIES**  
- **CONTACTS**  
- **WEB LINKS & ATTACHMENTS**

Each tab displays a different section of the project’s data.  
You can move between tabs at any time to review or update information.

---

#### 3. Update Project Data
Inside each tab, you may:

- View existing project details  
- Edit fields  
- Add or remove information  
- Upload or modify geometry  
- Update contacts, routes, or related links  

Any changes you make will be saved back to the **APEX Database** when you submit or save within that tab.

---

#### 4. Review Your Updates
Before leaving the editor, review each tab to ensure your updates are complete and accurate.  
Your changes will be stored directly in the APEX DB and reflected in downstream applications.

---

If you need to switch to a different project, simply return to the dropdown and select another one.
"""
}

def instructions(section):
    """
    Display the unified instructions inside a Streamlit expander.
    """
    content = TAB_INSTRUCTIONS[section]
    with st.expander("Instructions", expanded=False):
        st.markdown(content)
