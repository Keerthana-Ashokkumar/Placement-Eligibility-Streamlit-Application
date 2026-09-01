# =====================================
# 06_OOP_Implementation.py
# Project: Placement Eligibility Dashboard
# OOP Implementation
# =====================================

import streamlit as st
import pandas as pd
import sqlite3
import warnings

warnings.filterwarnings("ignore")

# ------------------------------
# 1️⃣ Database Manager Class
# ------------------------------
class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

# ------------------------------
# 2️⃣ Data Loader Class
# ------------------------------
class DataLoader:
    def __init__(self, conn):
        self.conn = conn

    def load_data(self):
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
        df = pd.read_sql_query(query, self.conn)
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

# ------------------------------
# 3️⃣ Filter Manager Class
# ------------------------------
class FilterManager:
    def __init__(self, df):
        self.df = df

    def filter_students(self, batches, min_prog, min_softskills, status):
        filtered = self.df[
            (self.df['course_batch'].isin(batches)) &
            (self.df['latest_project_score'] >= min_prog) &
            (self.df['avg_softskills'] >= min_softskills) &
            (self.df['placement_status'].isin(status))
        ]
        return filtered

# ------------------------------
# 4️⃣ Streamlit App
# ------------------------------
def main():
    st.set_page_config(page_title="Placement Eligibility Dashboard", layout="wide")
    st.title("🎯 Placement Eligibility Dashboard - OOP Version")

    db = DatabaseManager("placement_eligibility.db")
    conn = db.connect()
    st.success("✅ Connected to placement_eligibility.db")

    loader = DataLoader(conn)
    df = loader.load_data()

    # Sidebar Filters
    batches = st.sidebar.multiselect("Batch", df['course_batch'].unique(), default=df['course_batch'].unique())
    min_prog = st.sidebar.slider("Min Programming Score", int(df['latest_project_score'].min()), int(df['latest_project_score'].max()), 60)
    min_softskills = st.sidebar.slider("Min Avg Soft Skills", int(df['avg_softskills'].min()), int(df['avg_softskills'].max()), 60)
    status = st.sidebar.multiselect("Placement Status", df['placement_status'].unique(), default=df['placement_status'].unique())

    filter_mgr = FilterManager(df)
    filtered_df = filter_mgr.filter_students(batches, min_prog, min_softskills, status)

    st.subheader(f"✅ Eligible Students: {len(filtered_df)}")
    st.dataframe(filtered_df)

    # Individual Student Details
    selected_student = st.selectbox("Select Student", filtered_df['name'].unique())
    if selected_student:
        student_data = filtered_df[filtered_df['name']==selected_student].T
        student_data.columns = ["Value"]
        st.table(student_data)

    db.close()
    st.success("✅ Connection closed")

if __name__ == "__main__":
    main()
