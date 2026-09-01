# 05_Streamlit_Placement_Eligibility.py

import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

# Connect to SQLite
conn = sqlite3.connect("placement_eligibility.db")

# Page config
st.set_page_config(
    page_title="Placement Eligibility Dashboard",
    layout="wide"
)

st.title("🎯 Placement Eligibility Dashboard")
st.markdown("Filter students based on programming, soft skills, and placement readiness.")

# Load data
@st.cache_data
def load_data():
    query = """
        SELECT s.student_id, s.name, s.course_batch, s.age, s.gender,
               p.latest_project_score, p.problems_solved, p.mini_projects,
               ss.communication, ss.teamwork, ss.presentation, ss.leadership,
               ss.critical_thinking, ss.interpersonal_skills,
               pl.placement_status, pl.company_name, pl.placement_package
        FROM Students s
        LEFT JOIN Programming p ON s.student_id = p.student_id
        LEFT JOIN SoftSkills ss ON s.student_id = ss.student_id
        LEFT JOIN Placements pl ON s.student_id = pl.student_id
    """
    df = pd.read_sql_query(query, conn)
    df.fillna({
        'latest_project_score': 0,
        'problems_solved': 0,
        'mini_projects': 0,
        'communication': 0,
        'teamwork': 0,
        'presentation': 0,
        'leadership': 0,
        'critical_thinking': 0,
        'interpersonal_skills': 0,
        'placement_package': 0,
        'placement_status': 'Not Ready',
        'company_name': 'N/A'
    }, inplace=True)
    df['avg_softskills'] = df[['communication','teamwork','presentation','leadership','critical_thinking','interpersonal_skills']].mean(axis=1)
    return df

df = load_data()

# Sidebar filters
selected_batches = st.sidebar.multiselect("Batch", df['course_batch'].unique(), default=df['course_batch'].unique())
prog_score = st.sidebar.slider("Min Programming Score", int(df['latest_project_score'].min()), int(df['latest_project_score'].max()), 60)
softskills_score = st.sidebar.slider("Min Avg Soft Skills", int(df['avg_softskills'].min()), int(df['avg_softskills'].max()), 60)
selected_status = st.sidebar.multiselect("Placement Status", df['placement_status'].unique(), default=df['placement_status'].unique())

# Apply filters
filtered_df = df[
    (df['course_batch'].isin(selected_batches)) &
    (df['latest_project_score'] >= prog_score) &
    (df['avg_softskills'] >= softskills_score) &
    (df['placement_status'].isin(selected_status))
]

st.subheader(f"✅ Eligible Students: {len(filtered_df)}")
st.dataframe(filtered_df)

# Charts
st.markdown("### 📊 Insights")
st.bar_chart(filtered_df[['name','latest_project_score']].set_index('name'))
avg_soft_batch = filtered_df.groupby('course_batch')['avg_softskills'].mean().reset_index()
st.bar_chart(avg_soft_batch.set_index('course_batch'))

st.markdown("### 🔍 Individual Student Details")
selected_student = st.selectbox("Select Student", filtered_df['name'].unique())
if selected_student:
    student_data = filtered_df[filtered_df['name']==selected_student].T
    student_data.columns = ["Value"]
    st.table(student_data)
