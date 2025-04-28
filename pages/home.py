# pages/home.py
import streamlit as st
import plotly.express as px
import pandas as pd
from loader import courses, assessments, student_info, student_vle, student_assessment

# Page configuration
st.set_page_config(layout="wide")


# Convert ALL categorical columns to strings
def df_to_strings(df):
    return df.apply(lambda x: x.astype(str) if x.dtype == 'category' else x)

# Apply conversion to all dataframes
student_info = df_to_strings(student_info)
courses = df_to_strings(courses)
assessments = df_to_strings(assessments)
student_vle = df_to_strings(student_vle)
student_assessment = df_to_strings(student_assessment)

# Sidebar filters
with st.sidebar:
    st.title("🎛️ Filters")
    selected_presentations = st.multiselect(
        "Select Presentation(s)",
        options=student_info['code_presentation'].unique(),
        default=student_info['code_presentation'].unique()
    )

# Filter data
filtered_student_info = student_info[student_info['code_presentation'].isin(selected_presentations)].copy()
filtered_assessments = assessments[assessments['code_presentation'].isin(selected_presentations)].copy()
filtered_student_assessment = student_assessment.merge(
    filtered_student_info[['id_student']],
    on='id_student',
    how='inner'
).copy()

# =============================================
# DASHBOARD HEADER SECTION
# =============================================
st.title("📊 Open University At A Glance")
st.markdown("""
    <style>
    .metric-card {
        padding: 20px;
        border-radius: 12px;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #4e79a7;
        margin-bottom: 20px;
        height: 100%;
    }
    .metric-title {
        font-size: 14px;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 28px;
        color: #212529;
        font-weight: 700;
        margin: 10px 0;
    }
    .metric-chart {
        margin-top: 15px;
    }
    .double-card {
        grid-column: span 2;
    }
    </style>
""", unsafe_allow_html=True)

# Calculate metrics
total_students = len(student_info)
total_courses = len(courses['code_module'].unique())
active_students = len(filtered_student_info)
gender_dist = student_info['gender'].value_counts(normalize=True)
disability_rate = student_info['disability'].value_counts(normalize=True).get('Y', 0)
age_dist = student_info['age_band'].value_counts().nlargest(3)
presentation_dist = student_info['code_presentation'].value_counts()
result_dist = student_info['final_result'].value_counts(normalize=True)


# Create the dashboard grid
# col1, col2, col3 = st.columns([2,3,2])
# with col1:
#     # Student Metrics Card
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-title">Total Students</div>
#             <div class="metric-value">{total_students:,}</div>
#             <div class="metric-chart">
#                 {px.pie(names=gender_dist.index, values=gender_dist.values, hole=0.7, 
#                       color_discrete_sequence=['#4e79a7','#f28e2b'], width=180, height=180)
#                  .update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0))
#                  .update_traces(textinfo='none')
#                  .to_html(full_html=False)}
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

# with col2:
#     # Double-width Course Metrics Card
#     st.markdown(f"""
#         <div class="metric-card double-card">
#             <div class="metric-title">Course Distribution</div>
#             <div style="display: flex; justify-content: space-between;">
#                 <div style="width: 40%;">
#                     <div class="metric-value">{total_courses}</div>
#                     <div>Unique Courses</div>
#                 </div>
#                 <div style="width: 60%;">
#                     {px.bar(presentation_dist, orientation='h', 
#                            color_discrete_sequence=['#59a14f'])
#                      .update_layout(showlegend=False, margin=dict(t=20,b=20,l=20,r=20),
#                                   height=150, xaxis_visible=False)
#                      .update_yaxes(title=None)
#                      .to_html(full_html=False)}
#                 </div>
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

# with col3:
#     # Active Students Card
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-title">Currently Enrolled</div>
#             <div class="metric-value">{active_students:,}</div>
#             <div class="metric-chart">
#                 {px.line(x=filtered_student_info['code_presentation'].value_counts().index,
#                        y=filtered_student_info['code_presentation'].value_counts().values,
#                        markers=True, line_shape='spline',
#                        color_discrete_sequence=['#e15759'])
#                  .update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=150)
#                  .update_xaxes(title=None, visible=False)
#                  .update_yaxes(title=None, visible=False)
#                  .to_html(full_html=False)}
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

# # Second row
# col1, col2, col3 = st.columns([3,2,2])
# with col1:
#     # Age Distribution Card
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-title">Top Age Groups</div>
#             <div style="display: flex; gap: 20px;">
#                 <div style="width: 40%;">
#                     {px.pie(names=age_dist.index, values=age_dist.values, hole=0.5,
#                            color_discrete_sequence=['#76b7b2','#59a14f','#edc948'])
#                      .update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=150)
#                      .update_traces(textinfo='none')
#                      .to_html(full_html=False)}
#                 </div>
#                 <div style="width: 60%;">
#                     {px.bar(age_dist, orientation='v',
#                            color_discrete_sequence=['#76b7b2'])
#                      .update_layout(showlegend=False, margin=dict(t=20,b=20,l=20,r=20),
#                                   height=150, yaxis_visible=False)
#                      .update_xaxes(title=None)
#                      .to_html(full_html=False)}
#                 </div>
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

# with col2:
#     # Disability Card
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-title">Students with Disabilities</div>
#             <div class="metric-value">{disability_rate*100:.1f}%</div>
#             <div class="metric-chart">
#                 {px.bar(x=['With Disabilities'], y=[disability_rate*100],
#                        color_discrete_sequence=['#ff9da7'])
#                  .update_layout(showlegend=False, margin=dict(t=20,b=20,l=20,r=20),
#                               height=120, yaxis_range=[0,100])
#                  .update_xaxes(title=None)
#                  .update_yaxes(title=None, visible=False)
#                  .to_html(full_html=False)}
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

# with col3:
#     # Results Card
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-title">Success Rate</div>
#             <div class="metric-value">{result_dist.get('Pass', 0)*100:.1f}%</div>
#             <div class="metric-chart">
#                 {px.pie(names=result_dist.index, values=result_dist.values, hole=0.6,
#                       color_discrete_map={
#                           'Pass': '#59a14f',
#                           'Fail': '#e15759',
#                           'Withdrawn': '#edc948',
#                           'Distinction': '#4e79a7'
#                       })
#                  .update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=150)
#                  .update_traces(textinfo='none')
#                  .to_html(full_html=False)}
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

# Divider
st.markdown("---")

# =============================================
# PRE-ENROLLMENT CHARACTERISTICS SECTION
# =============================================
st.header("📋 Pre-Enrollment Characteristics")
st.markdown("Analyzing student demographics and background before course enrollment.")

# 1. Age Distribution
st.subheader("Age Distribution by Performance")
age_data = filtered_student_info[['age_band', 'final_result']].copy()
fig_age = px.histogram(
    age_data,
    x='age_band',
    color='final_result',
    barmode='group',
    color_discrete_map={
        'Withdrawn': '#FFC107',
        'Fail': '#F44336',
        'Pass': '#4CAF50',
        'Distinction': '#2196F3'
    },
    labels={'age_band': 'Age Group', 'count': 'Number of Students'},
    height=500
)
fig_age.update_layout(
    xaxis_title="Age Group",
    yaxis_title="Number of Students",
    legend_title="Final Result"
)
st.plotly_chart(fig_age, use_container_width=True)

# 2. Prior Education Impact
st.subheader("Prior Education vs Performance")
edu_data = filtered_student_info[['highest_education', 'final_result']].copy()
fig_edu = px.pie(
    edu_data,
    names='highest_education',
    facet_col='final_result',
    facet_col_wrap=2,
    height=900,  # Increased height for better spacing
    category_orders={'final_result': ['Pass', 'Distinction', 'Fail', 'Withdrawn']}
)
fig_edu.update_traces(
    textposition='inside',
    textinfo='percent+label',
    textfont_size=14
)
fig_edu.update_layout(
    margin=dict(t=100, b=100, l=50, r=50),  # Added margins for spacing
    uniformtext_minsize=12,
    uniformtext_mode='hide'
)
fig_edu.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
st.plotly_chart(fig_edu, use_container_width=True)

# 3. Gender Distribution
st.subheader("Gender Performance Breakdown")
gender_data = filtered_student_info[['gender', 'final_result']].copy()
fig_gender = px.sunburst(
    gender_data,
    path=['gender', 'final_result'],
    color='final_result',
    color_discrete_map={
        'Withdrawn': '#FFC107',
        'Fail': '#F44336', 
        'Pass': '#4CAF50',
        'Distinction': '#2196F3'
    },
    height=600
)
fig_gender.update_layout(margin=dict(t=0, b=0))
st.plotly_chart(fig_gender, use_container_width=True)

# =============================================
# ASSESSMENT PERFORMANCE SECTION (Preview)
# =============================================
st.header("📝 Assessment Performance Preview")
st.markdown("Early look at assessment patterns (full analysis in next section)")

# Assessment Scores by Gender
st.subheader("Gender Performance in Assessments")
merged_scores = pd.merge(
    pd.merge(filtered_student_assessment, filtered_assessments, on='id_assessment'),
    filtered_student_info[['id_student', 'gender']],
    on='id_student'
).copy()

fig_scores = px.box(
    merged_scores,
    x='assessment_type',
    y='score',
    color='gender',
    color_discrete_map={'M': '#4285F4', 'F': '#EA4335'},
    height=500,
    category_orders={'assessment_type': ['TMA', 'CMA', 'Exam']}
)
fig_scores.update_layout(
    xaxis_title="Assessment Type",
    yaxis_title="Score (%)",
    legend_title="Gender"
)
st.plotly_chart(fig_scores, use_container_width=True)

# Section divider
st.markdown("---")
st.markdown("💡 *Next sections will include detailed course engagement and VLE interaction analysis*")