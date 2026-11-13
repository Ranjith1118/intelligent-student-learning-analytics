from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "student_learning_data.csv"

REQUIRED_COLUMNS = {
    "student_id", "class_name", "subject", "score_pct", "attendance_pct",
    "assignments_assigned", "assignments_submitted", "quiz_avg_pct"
}

def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    numeric = [
        "score_pct", "attendance_pct", "assignments_assigned",
        "assignments_submitted", "quiz_avg_pct"
    ]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["student_id", "class_name", "subject", *numeric]).copy()
    df["submission_rate"] = (
        df["assignments_submitted"] /
        df["assignments_assigned"].clip(lower=1) * 100
    ).clip(0, 100)
    return df

def summarize_students(df):
    columns = [
        "student_id", "class_name", "avg_score", "attendance_pct",
        "submission_rate", "quiz_avg_pct"
    ]
    if df.empty:
        return pd.DataFrame(columns=columns)
    return df.groupby(["student_id", "class_name"], as_index=False).agg(
        avg_score=("score_pct", "mean"),
        attendance_pct=("attendance_pct", "mean"),
        submission_rate=("submission_rate", "mean"),
        quiz_avg_pct=("quiz_avg_pct", "mean"),
    )

def student_risk(row):
    signals = []
    if float(row.get("avg_score", row.get("score_pct", 0))) < 50:
        signals.append("assessment scores below 50%")
    if float(row.get("attendance_pct", 0)) < 75:
        signals.append("attendance below 75%")
    if float(row.get("submission_rate", 0)) < 70:
        signals.append("assignment submission below 70%")
    count = len(signals)
    level = "High" if count >= 2 else ("Moderate" if count == 1 else "Low")
    reason = (
        "Support signals: " + ", ".join(signals) + "."
        if signals else "No threshold-based support signals in the available data."
    )
    return {"level": level, "reason": reason}

def recommend_actions(row):
    actions = []
    if float(row.get("avg_score", 100)) < 60:
        actions.append("Offer a short, targeted revision session and practice questions.")
    if float(row.get("attendance_pct", 100)) < 80:
        actions.append("Have a private, supportive check-in to understand attendance barriers.")
    if float(row.get("submission_rate", 100)) < 75:
        actions.append("Break assignments into smaller milestones with reminders.")
    if not actions:
        actions.append("Discuss the student's goals and offer an optional enrichment activity.")
    actions.append("Review progress with the student and educator after an agreed period.")
    return actions

def subject_summary(df):
    columns = ["subject", "average_score", "average_attendance", "records"]
    if df.empty:
        return pd.DataFrame(columns=columns)
    return df.groupby("subject", as_index=False).agg(
        average_score=("score_pct", "mean"),
        average_attendance=("attendance_pct", "mean"),
        records=("student_id", "count"),
    ).round(1)
