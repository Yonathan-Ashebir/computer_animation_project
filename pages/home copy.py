# pages/home.py
import streamlit as st
from plotly import graph_objects as go  # For Sankey and advanced charts
import plotly.express as px  # For simpler charts
from loader import courses, assessments, student_info, student_vle, student_assessment
import pandas as pd

# Page title and description
st.title("🎓 Open University Analytics Dashboard")
st.markdown("""
Explore student performance across different courses and demographics.
Select a visualization from the options below.
""")

# Initialize session state for visualizations if not exists
if 'current_viz' not in st.session_state:
    st.session_state.current_viz = None

# Display data loading status
with st.status("Data loaded successfully!", state="complete"):
    st.write(f"✅ {len(courses)} courses")
    st.write(f"✅ {len(assessments)} assessments")
    st.write(f"✅ {len(student_info)} student records")

# pages/home.py
import streamlit as st
import plotly.express as px
from loader import student_info, courses


st.title("📊 Demographic Analysis")
st.markdown("---")

# 1. Gender vs Results Sunburst Chart
st.header("1. Gender Distribution by Final Result")

# Prepare data
plot_data = student_info[['gender', 'final_result']].copy()
plot_data['gender'] = plot_data['gender'].astype(str)
plot_data['final_result'] = plot_data['final_result'].astype(str)

# Create visualization
fig1 = px.sunburst(
    plot_data,
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

# Customize layout
fig1.update_layout(
    margin=dict(t=30, b=30),
    hoverlabel=dict(
        bgcolor="white",
        font_size=14
    )
)

st.plotly_chart(fig1, use_container_width=True)

# 2. Age Band Distribution
st.markdown("---")
st.header("2. Age Distribution by Result")

# Prepare data
age_data = student_info[['age_band', 'final_result']].copy()
age_data['age_band'] = age_data['age_band'].astype(str)

# Create visualization
fig2 = px.histogram(
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
    height=500,
    labels={'age_band': 'Age Group', 'count': 'Number of Students'}
)

# Customize layout
fig2.update_layout(
    xaxis_title="Age Group",
    yaxis_title="Number of Students",
    legend_title="Final Result"
)

st.plotly_chart(fig2, use_container_width=True)

# 3. Education Level Analysis
st.markdown("---")
st.header("3. Prior Education Impact")

# Prepare data
edu_data = student_info[['highest_education', 'final_result']].copy()
edu_data['highest_education'] = edu_data['highest_education'].astype(str)

# Create visualization
fig3 = px.pie(
    edu_data,
    names='highest_education',
    facet_col='final_result',
    facet_col_wrap=2,
    height=800,
    category_orders={
        'final_result': ['Pass', 'Fail', 'Withdrawn', 'Distinction']
    }
)

# Customize layout
fig3.update_traces(textposition='inside', textinfo='percent+label')
fig3.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

st.plotly_chart(fig3, use_container_width=True)

# 4. Assessment Scores by Gender
st.markdown("---")
st.header("4. Assessment Performance by Gender")

# Merge data
merged_gender = pd.merge(
    pd.merge(student_assessment, assessments, on='id_assessment'),
    student_info[['id_student', 'gender']],
    on='id_student'
)

# Create interactive box plot
fig4 = px.box(
    merged_gender,
    x='assessment_type',
    y='score',
    color='gender',
    labels={
        'assessment_type': 'Assessment Type', 
        'score': 'Score', 
        'gender': 'Gender'
    },
    category_orders={
        'assessment_type': ['TMA', 'CMA', 'Exam'],
        'gender': ['M', 'F']
    },
    color_discrete_map={
        'M': '#4285F4',  # Blue for Male
        'F': '#EA4335'   # Red for Female
    },
    height=500
)

# Add gender toggle dropdown
fig4.update_layout(
    updatemenus=[
        {
            'buttons': [
                {'method': 'update', 'label': 'All', 
                 'args': [{'visible': [True, True]}]},
                {'method': 'update', 'label': 'Male Only', 
                 'args': [{'visible': [True, False]}]},
                {'method': 'update', 'label': 'Female Only', 
                 'args': [{'visible': [False, True]}]}
            ],
            'direction': 'down',
            'showactive': True,
            'x': 1.15,
            'y': 1.15,
            'bgcolor': 'rgba(255,255,255,0.7)'
        }
    ],
    xaxis_title="Assessment Type",
    yaxis_title="Score (%)",
    legend_title="Gender",
    hovermode="x unified"
)

# Add median line annotation
fig4.add_hline(
    y=merged_gender['score'].median(),
    line_dash="dot",
    line_color="gray",
    annotation_text=f"Overall Median: {merged_gender['score'].median():.1f}%",
    annotation_position="bottom right"
)

st.plotly_chart(fig4, use_container_width=True)

# 2. Engagement and Behavioral Factors
st.markdown("---")
st.header("2. Engagement Analysis")

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

# 2.2 Attempt Flow Analysis
st.subheader("2.2 Outcome Pathways by Attempt History")

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

# 2.3 Weekly Engagement Patterns
st.subheader("2.3 Weekly Engagement Trends")

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


# 2.4 Withdrawal Risk Analysis
st.subheader("2.4 Withdrawal Probability by Course Progress")

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

# 3.1 Course Benchmarking
st.subheader("3.1 Course Benchmarking")

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

# 3.1 Score Distribution by Course
st.subheader("3.3 Course Score Distributions")

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
