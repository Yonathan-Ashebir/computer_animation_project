# pages/dataset.py
import streamlit as st
import pandas as pd
from loader import courses, assessments, student_info, student_vle, student_assessment

# Page configuration (MUST be first)
# st.set_page_config(
#     page_title="Dataset Explorer",
#     page_icon="📊",
#     layout="wide"
# )

# Page Header
st.title("📊 Dataset Explorer")

# =====================
# 1. Dataset Overview
# =====================
st.header("Dataset Overview")
st.markdown("""
This comprehensive dataset tracks anonymized student performance across the Open University's virtual learning environment.
It contains records for **32,593 students** in **22 courses**, with detailed information on:
- Assessment scores and submission patterns
- Virtual Learning Environment (VLE) interactions
- Demographic characteristics and enrollment history
- Course structures and presentation timelines

**Important Note**:  
The `student_info` table represents student enrollments in specific course (code_module, code_presentation) - not just personal details. This behavior is inherited from the original dataset.
For simplicity, this table has also been pre-merged with the original dataset's 'course_registration.csv'.
""")

# =====================
# 2. Dataset Health Dashboard
# =====================
st.header("📈 Dataset Health Metrics")

# Core metrics calculation
health_metrics = {
    "Tables": 5,
    "Total Students": f"{len(student_info):,}",
    "Assessment Records": f"{len(student_assessment):,}",
    "VLE Interactions": f"{student_vle['sum_click'].sum():,}",
    "Gender Balance": {
        "Male": f"{student_info['gender'].value_counts(normalize=True).mul(100).round(1)['M']}%",
        "Female": f"{student_info['gender'].value_counts(normalize=True).mul(100).round(1)['F']}%"
    }
}

# Metrics display
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Courses", len(courses['code_module'].unique()))
m2.metric("Academic Presentations", len(courses['code_presentation'].unique()))
m3.metric("Student Records", health_metrics['Total Students'])
m4.metric("Assessment Records", health_metrics['Assessment Records'])

# =====================
# 3. Interactive Data Explorer
# =====================
st.header("🔎 Interactive Data Explorer")


def show_dataset(df, name):
    # Multi-column sorting
    sort_cols = st.multiselect(
        f"Sort {name} by (priority order):",
        df.columns,
        key=f"sortcols_{name}"
    )
    
    # Sort directions for each column
    sort_directions = {}
    if sort_cols:
        with st.container():
            for i, col in enumerate(sort_cols):
                sort_directions[col] = st.radio(
                    f"Direction for '{col}'",
                    ["Ascending", "Descending"],
                    horizontal=True,
                    key=f"dir_{name}_{col}"
                )
    
    # Pagination controls
    page_size = st.selectbox(
        "Rows per page:", 
        [10, 25, 50, 100],
        key=f"pagesize_{name}"
    )
    
    # Apply sorting if columns selected
    if sort_cols:
        sort_bool = [sort_directions[col] == "Ascending" for col in sort_cols]
        sorted_df = df.sort_values(by=sort_cols, ascending=sort_bool)
    else:
        sorted_df = df.copy()
    
    # Pagination
    total_pages = len(sorted_df) // page_size + 1
    page_num = st.number_input(
        "Page number:",
        min_value=1,
        max_value=total_pages,
        value=1,
        key=f"page_{name}"
    )
    
    # Display styled table
    start_idx = (page_num - 1) * page_size
    end_idx = start_idx + page_size
    
    st.markdown(
        f"""
        <style>
            .dataframe {{
                width: 100%;
                font-size: 0.9em;
            }}
            .dataframe th {{
                background-color: #f0f2f6;
                text-align: left;
                padding: 8px;
            }}
            .dataframe td {{
                padding: 6px;
                border-bottom: 1px solid #ddd;
            }}
            .dataframe tr:hover {{
                background-color: #f5f5f5;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.dataframe(
        sorted_df.iloc[start_idx:end_idx],
        height=min(600, (page_size + 1) * 35),
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Showing rows {start_idx + 1} to {min(end_idx, len(df))} of {len(df):,}")

# Dataset selection
with st.expander("View Dataset"):
    dataset_choice = st.selectbox(
        "Choose dataset to explore:",
        ["Courses", "Assessments", "Student Info", "VLE Interactions", "Student Assessments"],
    )

    # Show selected dataset
    datasets = {
        "Courses": courses,
        "Assessments": assessments,
        "Student Info": student_info,
        "VLE Interactions": student_vle,
        "Student Assessments": student_assessment
    }

    show_dataset(datasets[dataset_choice], dataset_choice)

# =====================
# Footer
# =====================
st.markdown("---")
st.markdown("""
**Dataset Source**:  
[Open University Learning Analytics Dataset on Kaggle](https://www.kaggle.com/datasets/mohammadehsani/student-performance-at-open-university)  
*Use the interactive controls above to explore different sections of the dataset*
""", unsafe_allow_html=True)