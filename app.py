import streamlit as st
import pandas as pd
import plotly.express as px
import os
import zipfile
import requests
from io import BytesIO

# Constants
DATASET_URL = "https://www.kaggle.com/api/v1/datasets/download/mohammadehsani/student-performance-at-open-university"
DATA_DIR = "./data"
REQUIRED_FILES = [
    "courses.csv",
    "assessments.csv",
    "studentInfo.csv",
    "studentVle.csv",
    "studentAssessment.csv"
]

# --- Data Preparation ---
def download_dataset():
    """Download and extract dataset if missing"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    try:
        # Kaggle requires authentication - this may fail without credentials
        response = requests.get(DATASET_URL)
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(DATA_DIR)
        # st.success("Dataset downloaded and extracted successfully!")
    except Exception as e:
        st.error(f"Failed to download dataset: {str(e)}")
        st.info("Please manually download from Kaggle and place in ./data/")

def check_data_files():
    """Verify all required files exist"""
    missing_files = [f for f in REQUIRED_FILES if not os.path.exists(f"{DATA_DIR}/{f}")]
    if missing_files:
        download_dataset()
        # st.warning(f"Missing files: {', '.join(missing_files)}")
        # if st.button("Download dataset automatically"):
        #     download_dataset()
        # st.stop()

@st.cache_data
def load_data():
    check_data_files()
    return {
        "courses": pd.read_csv(f"{DATA_DIR}/courses.csv"),
        "assessments": pd.read_csv(f"{DATA_DIR}/assessments.csv"),
        "student_info": pd.read_csv(f"{DATA_DIR}/studentInfo.csv"),
        "student_vle": pd.read_csv(f"{DATA_DIR}/studentVle.csv"),
        "student_assessment": pd.read_csv(f"{DATA_DIR}/studentAssessment.csv")
    }

# --- Main App ---
def main():
    st.title("🎓 Open University Performance Analyzer")
    
    # Load data with progress indicator
    # with st.spinner("Loading data..."):
    data = load_data()
    
    # Merge datasets
    df = data["student_info"].merge(
        data["courses"], 
        on=["code_module", "code_presentation"], 
        how="left"
    )
    
    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    
    # Semester selection
    semesters = df["code_presentation"].unique()
    selected_semesters = st.sidebar.multiselect(
        "Select Semesters",
        options=semesters,
        default=semesters
    )
    
    # Gender filter for demographic chart
    gender_filter = st.sidebar.radio(
        "Gender Filter",
        options=["All", "Male", "Female"],
        index=0
    )
    
    # Filter data
    filtered_df = df[df["code_presentation"].isin(selected_semesters)]
    if gender_filter != "All":
        filtered_df = filtered_df[filtered_df["gender"] == gender_filter[0]]  # 'M' or 'F'

    # --- Visualizations ---
    tab1, tab2, tab3 = st.tabs(["Demographics", "Performance", "Engagement"])
    
    with tab1:
        # Enhanced Demographic Pie Chart
        st.subheader("🎯 Outcomes by Gender")
        
        if 'gender' in filtered_df.columns and 'final_result' in filtered_df.columns:
            # Create count data
            gender_results = filtered_df.groupby(["gender", "final_result"]).size().reset_index(name="count")
            
            fig = px.pie(
                gender_results,
                names="final_result",
                values="count",
                color="final_result",
                facet_col="gender",
                hole=0.4,
                category_orders={
                    "final_result": ["Distinction", "Pass", "Fail", "Withdrawn"],
                    "gender": ["M", "F"]
                },
                color_discrete_map={
                    "Distinction": "#4CAF50",
                    "Pass": "#8BC34A",
                    "Fail": "#F44336",
                    "Withdrawn": "#FFC107"
                }
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Required columns (gender/final_result) not found in data")

    with tab2:
        # Performance Analysis
        st.subheader("📊 Performance Metrics")
        
        # Assessment scores if available
        if 'student_assessment' in data:
            assessment_df = data["assessments"].merge(
                data["student_assessment"],
                on="id_assessment"
            ).merge(
                filtered_df[["id_student", "final_result"]],
                on="id_student"
            )
            
            if 'score' in assessment_df.columns:
                fig = px.box(
                    assessment_df.dropna(subset=["score"]),
                    x="assessment_type",
                    y="score",
                    color="final_result",
                    title="Score Distribution by Assessment Type"
                )
                st.plotly_chart(fig)
    
    with tab3:
        # Engagement Analysis
        st.subheader("🖱️ Engagement Metrics")
        
        if 'student_vle' in data:
            vle_data = data["student_vle"].merge(
                filtered_df[["id_student", "final_result"]],
                on="id_student"
            )
            clicks_by_result = vle_data.groupby(["final_result", "id_student"])["sum_click"].sum().reset_index()
            
            fig = px.box(
                clicks_by_result,
                x="final_result",
                y="sum_click",
                color="final_result",
                title="VLE Engagement by Final Result",
                category_orders={
                    "final_result": ["Distinction", "Pass", "Fail", "Withdrawn"]
                }
            )
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()