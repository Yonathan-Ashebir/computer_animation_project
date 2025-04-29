# app.py
import streamlit as st


# Define the pages (assuming files are in ./pages/)
home_page = st.Page(
    "pages/home.py",
    title="Home Dashboard",
    icon="🏠",
    default=True
)

dataset_page = st.Page(
    "pages/dataset.py",
    title="Dataset Explorer",
    icon="🔍"
)


# Set up navigation with custom styling
nav = st.navigation(
    [home_page, dataset_page],
    position="sidebar"
)

# Run the selected page
nav.run()

# Optional footer
# st.sidebar.markdown("---")
# st.sidebar.markdown(
#     "© 2025 Student Analytics | [GitHub](https://github.com/yourrepo)"
# )