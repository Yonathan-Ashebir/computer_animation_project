# pages/home.py
import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from loader import courses, assessments, student_info, student_vle, student_assessment

# Page configuration
st.set_page_config(
    page_title="Student Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
st.title("Overview")

# Define reusable style
card_style = """
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
"""

# Calculate metrics
total_students = len(student_info)
total_courses = len(courses['code_module'].unique())
active_students = len(filtered_student_info)
gender_dist = student_info['gender'].value_counts(normalize=True)
disability_rate = student_info['disability'].value_counts(normalize=True).get(True, 0)
age_dist = student_info['age_band'].value_counts().nlargest(3)
presentation_dist = student_info['code_presentation'].value_counts()
result_dist = student_info['final_result'].value_counts(normalize=True)

# Create the dashboard grid
col1, col2, col3 = st.columns([2, 3, 2])

# ========== COLUMN 1 ==========
with col1:
    # Student Metrics Card
    fig = go.Figure(
        data=[go.Pie(
            labels=gender_dist.index, 
            values=gender_dist.values, 
            hole=0.7,
            marker_colors=['#4e79a7', '#f28e2b'],
            textinfo='none'
        )]
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        width=180,
        height=180,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    html_text = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    components.html(f"""
        {card_style}
        <div class="metric-card">
            <div class="metric-title">Total Students</div>
            <div class="metric-value">{total_students:,}</div>
            <div class="metric-chart" style="width: 180px; height: 180px; margin: auto;">
                {html_text}
            </div>
        </div>
    """, height=300)

# ========== COLUMN 2 ==========
with col2:
    # Course Metrics Card
    fig = go.Figure(
        data=[go.Bar(
            y=presentation_dist.index,
            x=presentation_dist.values,
            orientation='h',
            marker_color='#59a14f'
        )]
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=150,
        xaxis_visible=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_yaxes(title=None)
    bar_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    components.html(f"""
        {card_style}
        <div class="metric-card">
            <div class="metric-title">Course Distribution</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="width: 40%; text-align: center;">
                    <div class="metric-value">{total_courses}</div>
                    <div style="color: #6c757d; font-size: 14px;">Unique Courses</div>
                </div>
                <div style="width: 60%;">
                    {bar_html}
                </div>
            </div>
        </div>
    """, height=250)

# ========== COLUMN 3 ==========
with col3:
    # Active Students Card
    fig = go.Figure(
        data=[go.Scatter(
            x=filtered_student_info['code_presentation'].value_counts().index,
            y=filtered_student_info['code_presentation'].value_counts().values,
            mode='lines+markers',
            line_shape='spline',
            marker_color='#e15759'
        )]
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=150,
        xaxis_visible=False,
        yaxis_visible=False,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    line_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    components.html(f"""
        {card_style}
        <div class="metric-card">
            <div class="metric-title">Currently Enrolled</div>
            <div class="metric-value">{active_students:,}</div>
            <div class="metric-chart">
                {line_html}
            </div>
        </div>
    """, height=300)

# ========== SECOND ROW ==========
col1, col2, col3 = st.columns([3, 2, 2])

# ========== COLUMN 1 ==========
with col1:
    # Age Distribution Card
    pie_fig = go.Figure(
        data=[go.Pie(
            labels=age_dist.index,
            values=age_dist.values,
            hole=0.5,
            marker_colors=['#76b7b2', '#59a14f', '#edc948'],
            textinfo='none'
        )]
    )
    pie_fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=150,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    pie_html = pie_fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    bar_fig = go.Figure(
        data=[go.Bar(
            x=age_dist.index,
            y=age_dist.values,
            marker_color='#76b7b2'
        )]
    )
    bar_fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=150,
        yaxis_visible=False,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    bar_html = bar_fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    components.html(f"""
        {card_style}
        <div class="metric-card">
            <div class="metric-title">Top Age Groups</div>
            <div style="display: flex; gap: 20px;">
                <div style="width: 40%;">
                    {pie_html}
                </div>
                <div style="width: 60%;">
                    {bar_html}
                </div>
            </div>
        </div>
    """, height=300)

# ========== COLUMN 2 ==========
with col2:
    # Disability Card
    fig = go.Figure(
        data=[go.Bar(
            x=[''],
            y=[disability_rate*100],
            marker_color='#ff9da7'
        )]
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=120,
        yaxis_range=[0,100],
        xaxis_visible=False,
        yaxis_visible=False,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    bar_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    components.html(f"""
        {card_style}
        <div class="metric-card">
            <div class="metric-title">Students with Disabilities</div>
            <div class="metric-value">{disability_rate*100:.1f}%</div>
            <div class="metric-chart">
                {bar_html}
            </div>
        </div>
    """, height=250)


# ========== COLUMN 3 ==========
with col3:
    # Results Card
    # Create ordered list of colors matching the result_dist index order
    color_map = {
        'Pass': '#59a14f',
        'Fail': '#e15759', 
        'Withdrawn': '#edc948',
        'Distinction': '#4e79a7'
    }
    ordered_colors = [color_map[result] for result in result_dist.index]
    
    fig = go.Figure(
        data=[go.Pie(
            labels=result_dist.index,
            values=result_dist.values,
            hole=0.6,
            marker_colors=ordered_colors,  # Now using a list of colors
            textinfo='none'
        )]
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=150,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    pie_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    components.html(f"""
        {card_style}
        <div class="metric-card">
            <div class="metric-title">Success Rate</div>
            <div class="metric-value">{result_dist.get('Pass', 0)*100:.1f}%</div>
            <div class="metric-chart">
                {pie_html}
            </div>
        </div>
    """, height=300)

# Divider
st.markdown("---")


# =============================================
# PRE-ENROLLMENT CHARACTERISTICS SECTION
# =============================================
st.header("📋 Pre-Enrollment Characteristics")
st.markdown("Analyzing student demographics and background before course enrollment.")

# =============================================
# IMD vs GENDER/AGE ANALYSIS HEATMAPS
# =============================================

# Prepare the data
analysis_df = student_info.copy()
analysis_df['passed'] = analysis_df['final_result'].isin(['Pass', 'Distinction']).astype(int)

# Create combined gender-age groups
analysis_df['gender_age'] = analysis_df['gender'] + ' - ' + analysis_df['age_band']

# Calculate pass rates by IMD and Gender-Age
pass_rates = analysis_df.groupby(['gender_age', 'imd_band'])['passed'].mean().unstack()

# Calculate average scores by IMD and Gender-Age
merged_scores = pd.merge(student_assessment, student_info[['id_student', 'gender', 'age_band', 'imd_band']], on='id_student')
merged_scores['gender_age'] = merged_scores['gender'] + ' - ' + merged_scores['age_band']
avg_scores = merged_scores.groupby(['gender_age', 'imd_band'])['score'].mean().unstack()

# Define color scales
pass_rate_colorscale = [[0, '#F44336'], [0.5, '#FFC107'], [1, '#4CAF50']]  # Red-Yellow-Green
score_colorscale = [[0, '#F44336'], [0.5, '#FFC107'], [1, '#4CAF50']]  # Red-Yellow-Green

# First Heatmap: Pass Rates
st.subheader("1.1. Pass Rate by IMD (x) vs Gender-Age Groups (y)")
fig_pass = go.Figure(data=go.Heatmap(
    z=pass_rates.values,
    x=pass_rates.columns,  # IMD bands on x-axis
    y=pass_rates.index,    # Gender-Age groups on y-axis
    colorscale=pass_rate_colorscale,
    zmin=0,
    zmax=1,
    colorbar=dict(title='Pass Rate', tickformat='.0%'),
    hovertemplate='<b>%{y}</b><br>IMD: %{x}<br>Pass Rate: %{z:.1%}<extra></extra>'
))
fig_pass.update_layout(
    xaxis_title='IMD Band',
    yaxis_title='Gender - Age Group',
    height=600,
    margin=dict(l=100)  # Extra space for y-axis labels
)
st.plotly_chart(fig_pass, use_container_width=True)



# Second Heatmap: Average Scores
st.subheader("1.2. Average Score by IMD (x) vs Gender-Age Groups (y)")
fig_score = go.Figure(data=go.Heatmap(
    z=avg_scores.values,
    x=avg_scores.columns,  # IMD bands on x-axis
    y=avg_scores.index,    # Gender-Age groups on y-axis
    colorscale=score_colorscale,


    colorbar=dict(title='Average Score'),
    hovertemplate='<b>%{y}</b><br>IMD: %{x}<br>Avg Score: %{z:.1f}<extra></extra>'
))
fig_score.update_layout(
    xaxis_title='IMD Band',
    yaxis_title='Gender - Age Group',
    height=600,
    margin=dict(l=100)  # Extra space for y-axis labels
)
st.plotly_chart(fig_score, use_container_width=True)

# Add interpretation guidance
st.markdown("""
**How to read these charts:**
- Each row represents a unique Gender-Age combination
- Each column represents an IMD band (socioeconomic status)
- Darker green indicates higher pass rates/scores
- Hover over cells for exact values
""")


st.subheader("1.3. Age Distribution by Performance")
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


import streamlit.components.v1 as components
from ipyvizzu import Data, Config, Style
from ipyvizzustory import Story, Slide, Step

# Subheader
st.subheader("1.4. Performance Distribution Breakdown")

# Prepare the data
result_counts = student_info.groupby(['final_result', 'gender', 'age_band']).size().reset_index(name='count')

# Create ipyvizzu data object
data = Data()
data.add_series("Result", result_counts['final_result'].tolist())
data.add_series("Gender", result_counts['gender'].tolist())
data.add_series("Age", result_counts['age_band'].tolist())
data.add_series("Count", result_counts['count'].tolist())

# Create story
story = Story(data=data)
story.set_size("100%", "400px")  # Responsive width, fixed height

# Custom style matching Streamlit aesthetics
custom_style = Style({
    "title": {"fontSize": "14px"},
    "plot": {
        "marker": {
            "colorPalette": "#4CAF50 #2196F3 #FFC107 #F44336",  # Green, Blue, Yellow, Red
            "label": {
                "fontSize": "12px",
                "color": "#333333"
            }
        },
        "xAxis": {"label": {"fontSize": "12px", "angle": -45}},
        "yAxis": {"label": {"fontSize": "12px"}}
    }
})

# Slide 1: Base view - Result counts
story.add_slide(
    Slide(
        Step(
            Config({
                "x": "Result", 
                "y": "Count",
                "title": "1. Overall Performance Distribution"
            }),
            custom_style
        )
    )
)

# Slide 2: Split by gender
story.add_slide(
    Slide(
        Step(
            Config({
                "x": "Result",
                "y": "Count",
                "color": "Gender",
                "split": True,
                "title": "2. Split by Gender (M/F)"
            }),
            custom_style
        )
    )
)

# Slide 3: Split by gender and age
story.add_slide(
    Slide(
        Step(
            Config({
                "x": "Result",
                "y": "Count",
                "color": "Gender",
                "split": "Age",
                "title": "3. Split by Gender & Age Groups"
            }),
            custom_style
        )
    )
)

# Add playback controls explanation
st.caption("Use the player controls to navigate through the animation steps")

# Render in Streamlit
components.html(
    story.to_html(),
    height=450,  # Slightly taller than the chart to accommodate controls
    scrolling=False
)

# Add interpretation guide
with st.expander("How to interpret this visualization", expanded=False):
    st.markdown("""
    This animated breakdown shows:
    - **Step 1**: Overall distribution of student outcomes
    - **Step 2**: How outcomes differ between genders
    - **Step 3**: How outcomes vary by both gender and age groups
    
    Colors represent:
    - 🟢 Pass | 🔵 Distinction | 🟡 Withdrawn | 🔴 Fail
    - Gender split: Darker shades = Male | Lighter shades = Female
    """)

st.subheader("1.5. Prior Education vs Performance")
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


st.subheader("1.6. Gender Performance Breakdown")
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


# Assessment Scores by Gender
st.subheader("1.7. Gender Performance in Assessments")
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


st.subheader("1.8 Outcome Pathways by Attempt History")

# Prepare data with meaningful attempt groups
attempt_flow = student_info.copy()

# Create smart grouping based on attempt distribution
attempt_counts = attempt_flow['num_of_prev_attempts'].value_counts().sort_index()

# Define logical groupings
if len(attempt_counts) > 4:
    bins = [0, 1, 2, 3, attempt_counts.index.max()+1]
    labels = ["First Attempt (0)", "Second Attempt (1)", "Third Attempt (2)", "4+ Attempts"]
else:
    bins = attempt_counts.index.tolist() + [attempt_counts.index.max()+1]
    labels = [f"{x} Attempts" for x in attempt_counts.index]

attempt_flow['attempt_group'] = pd.cut(
    attempt_flow['num_of_prev_attempts'],
    bins=bins,
    labels=labels,
    right=False
)

# Group data
grouped = attempt_flow.groupby(
    ['attempt_group', 'final_result']
).size().reset_index(name='count')

# Create nodes
all_nodes = grouped['attempt_group'].cat.categories.tolist() + ['Withdrawn', 'Fail', 'Pass', 'Distinction']

# Map indices
grouped['source_idx'] = grouped['attempt_group'].cat.codes
grouped['target_idx'] = grouped['final_result'].map({
    'Withdrawn': len(labels),
    'Fail': len(labels)+1,
    'Pass': len(labels)+2,
    'Distinction': len(labels)+3
})

# Create Sankey diagram
fig = go.Figure(go.Sankey(
    node=dict(
        pad=20,
        thickness=25,
        line=dict(color="black", width=0.7),
        label=all_nodes,
        color=px.colors.sequential.Oranges[:len(labels)] + ['#FFC107', '#F44336', '#4CAF50', '#2196F3']
    ),
    link=dict(
        source=grouped['source_idx'],
        target=grouped['target_idx'],
        value=grouped['count'],
        hovertemplate='%{source.label} → %{target.label}<br>Students: %{value:,}<extra></extra>'
    )
))

# Style layout
fig.update_layout(
    title_text="<b>Student Outcomes by Previous Attempts</b>",
    title_x=0.05,
    font_size=12,
    height=600,
    margin=dict(t=80, b=20),
    hoverlabel=dict(
        bgcolor="white",
        font_size=12
    )
)

# Add explanatory annotation
fig.add_annotation(
    x=0.5,
    y=-0.15,
    xref="paper",
    yref="paper",
    text="Width represents student count; Colors show attempt history",
    showarrow=False,
    font=dict(color="#666")
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# OUTCOME DISTRIBUTION DONUT CHART (FIXED ORDER)
# =============================================
st.header("1.9 Outcome Distribution")

# Define consistent color mapping and fixed order
CATEGORY_ORDER = ['Pass', 'Fail', 'Withdrawn', 'Distinction']
COLOR_MAP = {
    'Pass': '#59a14f',
    'Fail': '#e15759',
    'Withdrawn': '#edc948',
    'Distinction': '#4e79a7'
}

# Create filter controls in the right column
chart_col, filter_col = st.columns([3, 1])

with filter_col:
    st.markdown("### Filters")
    
    # Disability filter
    disability_status = st.radio(
        "Disability Status",
        options=["All", "Has Disability", "No Disability"],
        index=0
    )
    
    # Gender filter
    gender_options = ["All"] + sorted(student_info['gender'].dropna().unique().tolist())
    gender_filter = st.selectbox(
        "Gender",
        options=gender_options,
        index=0
    )

# Filter the data
filtered_data = student_info.copy()

if disability_status == "Has Disability":
    filtered_data = filtered_data[filtered_data['disability'] == True]
elif disability_status == "No Disability":
    filtered_data = filtered_data[filtered_data['disability'] == False]
    
if gender_filter != "All":
    filtered_data = filtered_data[filtered_data['gender'] == gender_filter]

# Calculate outcome distribution with fixed order
outcome_counts = filtered_data['final_result'].value_counts()
outcome_dist = outcome_counts.reindex(CATEGORY_ORDER, fill_value=0)  # Maintain order
outcome_pct = (outcome_dist / outcome_dist.sum()) * 100  # Convert to percentages
ordered_colors = [COLOR_MAP[result] for result in outcome_pct.index]  # Get colors in order

with chart_col:
    # Create and display donut chart
    fig = go.Figure(
        data=[go.Pie(
            labels=outcome_pct.index,
            values=outcome_pct.values,
            hole=0.6,
            marker_colors=ordered_colors,
            textinfo='label+percent',
            textposition='inside',
            insidetextorientation='radial',
            sort=False  # Disable automatic sorting
        )]
    )
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=500,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(
        hoverinfo='label+percent',
        textfont_size=14,
        marker_line=dict(width=1, color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Showing results for {len(filtered_data)} students")

    # Add hidden table to verify order (for debugging)
    if st.checkbox("Show data table", False):
        st.dataframe(outcome_pct.reset_index().rename(columns={
            'index': 'Outcome',
            'final_result': 'Percentage'
        }))


# =============================================
# POST-ENROLLMENT FACTORS SECTION
# =============================================
st.markdown("---")
st.header("2. Post-Enrollment Factors")

# --- VLE Engagement by Outcome ---
st.subheader("2.1 Engagement by Final Result")

if 'sum_click' in student_vle.columns:
    engagement = (
        student_vle.merge(
            student_info[['id_student', 'final_result']], 
            on='id_student'
        )
        .groupby(['id_student', 'final_result'])['sum_click']
        .sum()
        .reset_index()
    )
    
    fig = px.box(
        engagement,
        x='final_result',
        y='sum_click',
        color='final_result',
        category_orders={'final_result': ['Withdrawn', 'Fail', 'Pass', 'Distinction']},
        color_discrete_map={
            'Withdrawn': '#FFC107',
            'Fail': '#F44336', 
            'Pass': '#4CAF50',
            'Distinction': '#2196F3'
        },
        labels={'sum_click': 'Total VLE Clicks', 'final_result': 'Outcome'}
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Engagement data not available")


# 2.2 Weekly Engagement Patterns
st.subheader("2.2 Weekly Engagement Trends")

# Calculate weekly activity
weekly_activity = student_vle.merge(
    student_info[['id_student', 'final_result']],
    on='id_student'
)
weekly_activity['week'] = (weekly_activity['date'] // 7) + 1

# Aggregate data
weekly_avg = weekly_activity.groupby(
    ['week', 'final_result']
)['sum_click'].mean().reset_index()

# Create line chart
fig_weekly = px.line(
    weekly_avg,
    x='week',
    y='sum_click',
    color='final_result',
    color_discrete_map={
        'Withdrawn': '#FFC107',
        'Fail': '#F44336', 
        'Pass': '#4CAF50',
        'Distinction': '#2196F3'  # Using your standard blue instead of dark green
    },
    labels={
        'sum_click': 'Average Weekly Clicks', 
        'week': 'Week of Course',
        'final_result': 'Outcome'
    },
    height=500
)

# Enhanced styling
fig_weekly.update_layout(
    xaxis_title="Week of Course",
    yaxis_title="Average VLE Interactions",
    hovermode="x unified",
    legend_title_text="Final Result",
    xaxis=dict(
        tickmode='linear',
        dtick=1,
        range=[1, weekly_activity['week'].max()]
    ),
    plot_bgcolor='rgba(0,0,0,0.05)'
)

# Add critical period annotation (highest divergence point)
max_week = weekly_avg.loc[weekly_avg.groupby('week')['sum_click'].std().idxmax()]
fig_weekly.add_vline(
    x=max_week.name,
    line_dash="dot",
    line_color="grey",
    annotation_text=f"Week {max_week.name}: Peak divergence",
    annotation_position="top right"
)

st.plotly_chart(fig_weekly, use_container_width=True)

# Add explanatory note
st.caption("""
Shows average weekly engagement in the Virtual Learning Environment (VLE). 
Critical periods marked where engagement patterns diverge most between outcome groups.
""")


# 2.3 Withdrawal Risk Analysis
st.subheader("2.3 Withdrawal Probability by Course Progress")

# Calculate course progress (assuming timeline_data exists from earlier)
timeline_data = student_vle.merge(
    student_info[['id_student', 'code_module', 'code_presentation', 'final_result', 'date_registration']].merge(
        courses[['code_module', 'code_presentation', 'module_presentation_length']],
        on=['code_module', 'code_presentation']
    ),
    on=['id_student', 'code_module', 'code_presentation']
).assign(
    progress=lambda x: 100 * (x['date'] - x['date_registration']) / x['module_presentation_length']
)

# Bin into checkpoints (0-10%, 10-20%, etc.)
timeline_data['checkpoint'] = pd.cut(
    timeline_data['progress'],
    bins=range(0, 101, 10),
    labels=[f"{i}-{i+10}%" for i in range(0, 100, 10)],
    right=False
)

# Calculate withdrawal rates
withdrawal_rates = (
    timeline_data.groupby(['checkpoint', 'id_student'])
    ['final_result'].first()
    .eq('Withdrawn')
    .groupby('checkpoint')
    .agg(['mean', 'count'])
    .rename(columns={'mean': 'withdrawal_prob', 'count': 'students_at_risk'})
    .reset_index()
)

# Create area chart
fig_withdrawal = go.Figure()

fig_withdrawal.add_trace(go.Scatter(
    x=withdrawal_rates['checkpoint'],
    y=withdrawal_rates['withdrawal_prob']*100,
    fill='tozeroy',
    mode='lines+markers',
    line=dict(color='#F44336', width=3),
    fillcolor='rgba(244, 67, 54, 0.2)',
    hovertemplate=(
        '<b>%{x}</b><br>'
        'Withdrawal Rate: %{y:.1f}%<br>'
        'Students at Risk: %{customdata:,}<extra></extra>'
    ),
    customdata=withdrawal_rates['students_at_risk'],
    name='Withdrawal Rate'
))

# Add peak annotation
max_rate = withdrawal_rates['withdrawal_prob'].max() * 100
max_checkpoint = withdrawal_rates.loc[withdrawal_rates['withdrawal_prob'].idxmax(), 'checkpoint']
fig_withdrawal.add_annotation(
    x=max_checkpoint,
    y=max_rate + 3,
    text=f"Critical Period: {max_rate:.1f}%",
    showarrow=True,
    arrowhead=2,
    ax=0,
    ay=-40,
    font=dict(size=12)
)

# Add overall average
avg_rate = withdrawal_rates['withdrawal_prob'].mean() * 100
fig_withdrawal.add_hline(
    y=avg_rate,
    line_dash="dot",
    line_color="gray",
    annotation_text=f"Average: {avg_rate:.1f}%", 
    annotation_position="bottom right"
)

# Style layout
fig_withdrawal.update_layout(
    xaxis_title="Course Completion (%)",
    yaxis_title="Withdrawal Probability (%)",
    hovermode="x unified",
    height=500,
    margin=dict(t=40),
    showlegend=False
)

st.plotly_chart(fig_withdrawal, use_container_width=True)

# Key insight box
st.info(f"""
**Key Insight**: Highest withdrawal risk occurs at **{max_checkpoint}** completion ({max_rate:.1f}% rate). 
Early interventions before this point may improve retention.
""")

# 2.4 Course Benchmarking
st.subheader("2.4 Course Benchmarking")

# Calculate real course metrics
course_metrics = (
    student_info.groupby('code_module')
    .agg(
        Enrollment=('id_student', 'nunique'),
        Pass_Rate=('final_result', lambda x: (x.isin(['Pass', 'Distinction'])).mean() * 100),
        Avg_Score=('id_student', lambda x: student_assessment[
            student_assessment['id_student'].isin(x)
        ]['score'].mean())
    )
    .reset_index()
    .rename(columns={'code_module': 'Course'})
)

# Visualizations
col1, col2 = st.columns(2)

with col1:
    fig_pass = px.bar(
        course_metrics,
        x='Course',
        y='Pass_Rate',
        color='Course',
        title='Pass Rates by Course',
        labels={'Pass_Rate': 'Pass Rate (%)'},
        height=400
    )
    st.plotly_chart(fig_pass, use_container_width=True)

with col2:
    fig_scatter = px.scatter(
        course_metrics,
        x='Enrollment',
        y='Avg_Score',
        size='Pass_Rate',
        color='Course',
        hover_name='Course',
        title='Enrollment vs Performance',
        labels={
            'Avg_Score': 'Average Score (%)',
            'Enrollment': 'Number of Students',
            'Pass_Rate': 'Pass Rate (%)'
        },
        height=400
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# Your exact metrics layout - now with REAL data
st.subheader("Key Statistics")
cols = st.columns(4)
cols[0].metric("Total Courses", len(course_metrics))
cols[1].metric("Avg Pass Rate", f"{course_metrics['Pass_Rate'].mean():.1f}%")
cols[2].metric("Highest Enrollment", course_metrics['Enrollment'].max())
cols[3].metric("Top Scoring Course", 
              course_metrics.loc[course_metrics['Avg_Score'].idxmax()]['Course'],
              delta=f"{course_metrics['Avg_Score'].max():.1f} pts")

# Raw data toggle (now shows real data)
if st.checkbox("Show course metrics data"):
    st.dataframe(
        course_metrics.style.format({
            'Pass_Rate': '{:.1f}%',
            'Avg_Score': '{:.1f}'
        }),
        hide_index=True,
        column_config={
            "Course": "Course Code",
            "Enrollment": st.column_config.NumberColumn("Students"),
            "Pass_Rate": st.column_config.NumberColumn("Pass Rate %"),
            "Avg_Score": st.column_config.NumberColumn("Avg Score")
        }
    )

# 2.5 Score Distribution by Course
st.subheader("2.5 Course Score Distributions")

# Merge and plot
merged_scores = pd.merge(student_assessment, assessments, on='id_assessment')
fig_course = px.box(
    merged_scores,
    x='code_module',
    y='score',
    color='code_module',
    labels={'code_module': 'Course', 'score': 'Score (%)'},
    category_orders={'code_module': sorted(merged_scores['code_module'].unique())},
    height=500
)

# Add horizontal mean line
mean_score = merged_scores['score'].mean()
fig_course.add_hline(
    y=mean_score,
    line_dash="dot",
    line_color="gray",
    annotation_text=f"Mean: {mean_score:.1f}%",
    annotation_position="bottom right"
)

# Style layout
fig_course.update_layout(
    showlegend=False,
    xaxis_title="Course Code",
    yaxis_title="Assessment Score (%)",
    hovermode="x unified"
)

st.plotly_chart(fig_course, use_container_width=True)


# import streamlit as st
# import streamlit.components.v1 as components
# from ipyvizzu import Data, Config
# from ipyvizzustory import Story, Slide, Step

# # Prepare data
# data = Data()
# data.add_series("Category", ["A", "B", "C"])
# data.add_series("Value", [10, 20, 30])

# # Create story
# story = Story(data=data)
# slide = Slide(Step(Config({"x": "Category", "y": "Value"})))
# story.add_slide(slide)

# # Export to HTML
# html = story.to_html()

# # Render in Streamlit
# components.html(html, height=500, scrolling=True)

# import streamlit as st
# import streamlit.components.v1 as components
# from ipyvizzu import Data, Config
# from ipyvizzustory import Story, Slide, Step

# # Prepare data
# data = Data()
# data.add_series("Category", ["A", "B", "C"])
# data.add_series("Value", [10, 20, 30])

# # Create story
# story = Story(data=data)

# # First step (your original)
# slide1 = Slide(Step(Config({"x": "Category", "y": "Value"})))
# story.add_slide(slide1)

# # Second step (new - Pie chart)
# slide2 = Slide(Step(Config({"angle": "Value", "geometry": "circle", "color": "Category"})))
# story.add_slide(slide2)

# # Export to HTML
# html = story.to_html()

# # Render in Streamlit
# components.html(html, height=500, scrolling=True)

