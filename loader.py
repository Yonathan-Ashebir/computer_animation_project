from io import BytesIO
import zipfile
import pandas as pd
import plotly.express as px
import os
import requests
import streamlit as st

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

@st.cache_resource
def load_data():
    check_data_files()
    # Define ordered categories
    result_order = ['Withdrawn', 'Fail', 'Pass', 'Distinction']
    age_band_order = ['0-35', '35-55', '55<=']
    imd_band_order = [
        '0-10%', '10-20%', '20-30%', '30-40%', 
        '40-50%', '50-60%', '60-70%', '70-80%', 
        '80-90%', '90-100%'
    ]
    
    # Load data with initial types
    data = {
        "courses": pd.read_csv(f"{DATA_DIR}/courses.csv"),
        "assessments": pd.read_csv(
            f"{DATA_DIR}/assessments.csv",
            dtype={
                'id_assessment': 'int32',
                'code_module': 'category',
                'code_presentation': 'category',
                'assessment_type': 'category', 
                'date': 'Int32'
            }
        ),
        "student_info": pd.read_csv(
            f"{DATA_DIR}/studentInfo.csv",
            dtype={
                'id_student': 'int32',
                'gender': 'category',
                'region': 'category',
                'highest_education': 'category',
                # 'disability': 'boolean'
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

    # --- Assessment Date Imputation ---
    if 'date' in data["assessments"].columns:
        # Convert to numeric, coercing errors to NaN
        data["assessments"]['date'] = pd.to_numeric(data["assessments"]['date'], errors='coerce')
        
        # Calculate mean dates by assessment type
        mean_dates = data["assessments"].groupby('assessment_type')['date'].mean().round().astype('int32')
        
        # Impute missing dates with type-specific averages
        missing_dates = data["assessments"]['date'].isna()
        data["assessments"].loc[missing_dates, 'date'] = data["assessments"][missing_dates]['assessment_type'].map(mean_dates)

        
        # Convert to int32 after imputation
        data["assessments"]['date'] = data["assessments"]['date'].astype('int32')

    # --- Student Info Categorical Conversions ---
    data["student_info"]['final_result'] = pd.Categorical(
        data["student_info"]['final_result'],
        categories=result_order,
        ordered=True
    )
    
    data["student_info"]['age_band'] = pd.Categorical(
        data["student_info"]['age_band'],
        categories=age_band_order,
        ordered=True
    )
    
    data["student_info"]['imd_band'] = pd.Categorical(
        data["student_info"]['imd_band'],
        categories=imd_band_order,
        ordered=True
    )

    student_registration = pd.read_csv(f"{DATA_DIR}/studentRegistration.csv", dtype={'date_registration': 'Int32', 'date_unregistration': 'Int32'})
    data['student_info'] = data['student_info'].merge(
        student_registration[['code_module', 'code_presentation', 'id_student', 
                            'date_registration', 'date_unregistration']],
        on=['code_module', 'code_presentation', 'id_student'],
        how='left'
    )
    
    
    # Convert disability Y/N to boolean
    if 'disability' in data["student_info"].columns:
        data["student_info"]['disability'] = data["student_info"]['disability'].map({'Y': True, 'N': False})
    
    return data
if 'data' not in globals():
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