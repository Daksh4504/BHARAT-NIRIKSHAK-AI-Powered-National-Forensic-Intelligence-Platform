"""App entry point and page registry.

Run with::

    streamlit run streamlit_app.py
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Ahmedabad crime concentration",
    page_icon=":material/location_on:",
    layout="wide",
    initial_sidebar_state="expanded",
)

page = st.navigation(
    [
        st.Page("app_pages/overview.py", title="Overview", icon=":material/dashboard:"),
        st.Page(
            "app_pages/spatial.py",
            title="Spatial analysis",
            icon=":material/grid_view:",
        ),
        st.Page(
            "app_pages/temporal.py",
            title="Temporal analysis",
            icon=":material/insights:",
        ),
        st.Page(
            "app_pages/risk_map.py",
            title="Risk map",
            icon=":material/map:",
        ),
        st.Page(
            "app_pages/methodology.py",
            title="Methodology",
            icon=":material/science:",
        ),
    ]
)

page.run()
