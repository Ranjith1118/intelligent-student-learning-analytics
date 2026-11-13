import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from modules.analytics import (
    load_data, summarize_students, student_risk, recommend_actions, subject_summary
)
from modules.prompts import compare_prompts, chatbot_answer

# Load optional environment configuration from the project root.
load_dotenv()

st.set_page_config(
    page_title="Intelligent Student Learning Analytics",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Intelligent Student Learning Analytics Platform")
st.caption(
    "Educational support prototype using synthetic demonstration data. "
    "Do not use its simple support indicators for high-stakes decisions."
)

try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.info("Check that data/student_learning_data.csv exists in the project folder.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    class_values = sorted(df["class_name"].dropna().astype(str).unique().tolist())
    selected_class = st.selectbox("Class / cohort", ["All"] + class_values)
    subject_values = sorted(df["subject"].dropna().astype(str).unique().tolist())
    selected_subject = st.selectbox("Subject", ["All"] + subject_values)
    min_attendance = st.slider("Minimum attendance (%)", 0, 100, 0)

filtered = df.copy()
if selected_class != "All":
    filtered = filtered[filtered["class_name"] == selected_class]
if selected_subject != "All":
    filtered = filtered[filtered["subject"] == selected_subject]
filtered = filtered[filtered["attendance_pct"] >= min_attendance]

tabs = st.tabs([
    "Overview dashboard",
    "Student insights",
    "Intervention planner",
    "Prompt lab",
    "Learning chatbot",
    "Data & methodology",
])

with tabs[0]:
    st.subheader("Learning analytics overview")
    if filtered.empty:
        st.warning("No records match the selected filters. Try lowering the attendance filter.")
    else:
        summary = summarize_students(filtered)
        high_count = sum(
            student_risk(row)["level"] == "High" for _, row in summary.iterrows()
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Students", int(filtered["student_id"].nunique()))
        c2.metric("Average score", f"{filtered['score_pct'].mean():.1f}%")
        c3.metric(
            "Average attendance",
            f"{filtered.groupby('student_id')['attendance_pct'].mean().mean():.1f}%"
        )
        c4.metric("High support signals", int(high_count))

        left, right = st.columns(2)
        with left:
            score_frame = filtered.groupby("student_id", as_index=False)["score_pct"].mean()
            fig = px.histogram(
                score_frame, x="score_pct", nbins=10,
                title="Distribution of average student scores",
                labels={"score_pct": "Average score (%)"}
            )
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.scatter(
                filtered, x="attendance_pct", y="score_pct", color="subject",
                hover_data=["student_id"],
                title="Attendance vs assessment score",
                labels={"attendance_pct": "Attendance (%)", "score_pct": "Assessment score (%)"}
            )
            st.plotly_chart(fig, use_container_width=True)

        subj = subject_summary(filtered)
        st.plotly_chart(
            px.bar(subj, x="subject", y="average_score",
                   title="Average score by subject",
                   labels={"average_score": "Average score (%)"}),
            use_container_width=True
        )
        st.dataframe(subj, use_container_width=True, hide_index=True)

with tabs[1]:
    st.subheader("Student-level insights")
    summary = summarize_students(filtered)
    if summary.empty:
        st.info("No students match the current filters.")
    else:
        chosen_student = st.selectbox(
            "Choose a demonstration student", summary["student_id"].tolist()
        )
        row = summary[summary["student_id"] == chosen_student].iloc[0]
        signal = student_risk(row)
        st.metric("Support priority (rule-based)", signal["level"])
        st.write(signal["reason"])
        st.write(
            f"Average score: **{row['avg_score']:.1f}%** · "
            f"Attendance: **{row['attendance_pct']:.1f}%** · "
            f"Assignment submission: **{row['submission_rate']:.1f}%**"
        )
        st.markdown("**Suggested supportive actions**")
        for action in recommend_actions(row):
            st.write(f"- {action}")
        st.caption(
            "These transparent demo rules are not a diagnosis or validated prediction. "
            "Discuss context with the student and educator."
        )

with tabs[2]:
    st.subheader("Intervention planner")
    summary = summarize_students(filtered)
    if summary.empty:
        st.info("No students are available for this filter selection.")
    else:
        plan_rows = []
        order = {"High": 0, "Moderate": 1, "Low": 2}
        for _, row in summary.iterrows():
            signal = student_risk(row)
            actions = recommend_actions(row)
            plan_rows.append({
                "Student": row["student_id"],
                "Class": row["class_name"],
                "Average score (%)": round(row["avg_score"], 1),
                "Attendance (%)": round(row["attendance_pct"], 1),
                "Submission rate (%)": round(row["submission_rate"], 1),
                "Support priority": signal["level"],
                "Suggested action": actions[0],
                "_order": order[signal["level"]],
            })
        plan_df = pd.DataFrame(plan_rows).sort_values(
            ["_order", "Average score (%)"], ascending=[True, True]
        ).drop(columns=["_order"])
        st.dataframe(plan_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download intervention plan CSV",
            data=plan_df.to_csv(index=False).encode("utf-8"),
            file_name="student_intervention_plan.csv",
            mime="text/csv",
        )

with tabs[3]:
    st.subheader("Prompt templates and comparison")
    prompt_question = st.text_area(
        "Learning support question",
        "Suggest a supportive study plan for a student with low quiz scores and inconsistent attendance."
    )
    context = {
        "average_score": 58,
        "attendance_pct": 72,
        "submission_rate": 65,
        "subject": selected_subject,
    }
    if st.button("Compare prompt versions"):
        for label, prompt in compare_prompts(prompt_question, context).items():
            with st.expander(label, expanded=True):
                st.code(prompt, language="text")
        st.caption("Prompts are shown for learning and are not sent to an external AI model.")

with tabs[4]:
    st.subheader("Learning support chatbot")
    chat_question = st.text_area(
        "Ask about study planning, revision, time management, or learning strategies"
    )
    if st.button("Get learning guidance"):
        if chat_question.strip():
            st.markdown(chatbot_answer(chat_question))
        else:
            st.warning("Enter a question first.")

with tabs[5]:
    st.subheader("Data and methodology")
    st.write("The included dataset contains synthetic demonstration records, not real student data.")
    st.write(
        "Support levels use simple thresholds for assessment score, attendance, "
        "and assignment submission. They are not a trained machine-learning model."
    )
    st.write(
        "Use analytics to offer support, not to label or punish students. "
        "Protect real student data and follow applicable privacy requirements."
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download sample dataset CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="sample_student_learning_data.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Educational prototype · Synthetic data · No validated predictive model · "
    "No external AI API required for the included features."
)
