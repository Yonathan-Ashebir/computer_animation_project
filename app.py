import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration
DATASET_URL = "https://www.kaggle.com/api/v1/datasets/download/mohammadehsani/student-performance-at-open-university"
DATA_DIR = "./data"
REQUIRED_FILES = [
    "courses.csv",
    "assessments.csv",
    "studentInfo.csv",
    "studentVle.csv",
    "studentAssessment.csv"
]

# --- Data Loading ---
@st.cache_data(ttl=3600)
def load_data():
    # Define ordered categories for final_result
    result_order = ['Withdrawn', 'Fail', 'Pass', 'Distinction']
    
    data = {
        "courses": pd.read_csv(f"{DATA_DIR}/courses.csv"),
        "assessments": pd.read_csv(f"{DATA_DIR}/assessments.csv"),
        "student_info": pd.read_csv(
            f"{DATA_DIR}/studentInfo.csv",
            dtype={
                'id_student': 'int32',
                'gender': 'category',
                'region': 'category',
                'highest_education': 'category'
            }
        ),
        "student_vle": pd.read_csv(
            f"{DATA_DIR}/studentVle.csv",
            dtype={'id_student': 'int32', 'sum_click': 'int16'}
        ),
        "student_assessment": pd.read_csv(
            f"{DATA_DIR}/studentAssessment.csv",
            dtype={'id_student': 'int32', 'score': 'float32'}
        )
    }
    
    # Convert final_result to ordered categorical
    data["student_info"]['final_result'] = pd.Categorical(
        data["student_info"]['final_result'],
        categories=result_order,
        ordered=True
    )

    student_registration = pd.read_csv(f"{DATA_DIR}/studentRegistration.csv")
    data['student_info'] = data['student_info'].merge(
        student_registration[['code_module', 'code_presentation', 'id_student', 
                            'date_registration', 'date_unregistration']],
        on=['code_module', 'code_presentation', 'id_student'],
        how='left'
    )
    
    return data

# --- Page Config ---
st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="🎓",
    layout="wide"
)

# --- First Visualization Section ---
def main():
    data = load_data()
    (
        courses,          # DataFrame with course/module info
        assessments,      # DataFrame with exam/assignment details
        student_info,     # DataFrame with student demographics and results
        student_vle,      # DataFrame with virtual learning environment interactions
        student_assessment # DataFrame with student scores for assessments
    ) = (
        data["courses"],
        data["assessments"],
        data["student_info"],
        data["student_vle"],
        data["student_assessment"]
    )
    
    st.title("Student Performance Analysis")
    
    # Outcome Distribution
    st.header("1. Outcome Analysis by Gender")
    
    # Create sorted sunburst data
    plot_data = student_info[['gender', 'final_result']].copy()
    plot_data['gender'] = plot_data['gender'].astype(str)
    plot_data['final_result'] = plot_data['final_result'].astype(str)

    # 2. Create the damn chart
    fig = px.sunburst(
        plot_data,
        path=['gender', 'final_result'],
        color='final_result',
        color_discrete_map={
            'Withdrawn': '#FFC107',
            'Fail': '#F44336', 
            'Pass': '#4CAF50',
            'Distinction': '#2196F3'
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)

    if 'score' in student_assessment.columns:
        merged_scores = (
            assessments.merge(student_assessment, on='id_assessment')
            .merge(student_info[['id_student', 'gender']], on='id_student')
        )
        merged_scores['gender'] = merged_scores['gender'].astype(str)
        
        fig3 = px.box(
            merged_scores.dropna(subset=['score']),
            x='assessment_type',
            y='score',
            color='gender',
            points='all',
            title='Assessment Scores by Type and Gender'
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        print("Score column not found in student_assessment DataFrame")

if __name__ == "__main__":
    main()