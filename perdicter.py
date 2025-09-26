import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 1. Page Setup
st.set_page_config(page_title="Student Pass/Fail Predictor", layout="centered")
st.title("🎓 Student Pass/Fail Predictor")
st.caption("Predict for one or many students.")

# 2. Generate Simulated Training Data
np.random.seed(42)
num_samples = 500

study_hours = np.random.uniform(0, 6, num_samples)
attendance = np.random.randint(40, 101, num_samples)
assignment_score = np.random.randint(0, 101, num_samples)

# Custom logic to define pass/fail
def logic_label(hours, att, assign):
    return 1 if hours >= 2.5 and att >= 65 and assign >= 45 else 0

labels = [logic_label(h, a, s) for h, a, s in zip(study_hours, attendance, assignment_score)]

# Build dataframe
df = pd.DataFrame({
    "Study_Hours": study_hours,
    "Attendance": attendance,
    "Assignment_Score": assignment_score,
    "Result": labels
})

# Limit pass rate to 60%
pass_df = df[df["Result"] == 1].sample(frac=0.6, random_state=1)
fail_df = df[df["Result"] == 0]
balanced_df = pd.concat([pass_df, fail_df]).sample(frac=1, random_state=42).reset_index(drop=True)

# 3. Train the ML Model
X = balanced_df[["Study_Hours", "Attendance", "Assignment_Score"]]
y = balanced_df["Result"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

model = RandomForestClassifier()
model.fit(X_train, y_train)

# 4. User Input Mode
mode = st.radio("Select Input Mode:", ["Single Student", "Multiple Students"])

# 5. Single Student Mode
if mode == "Single Student":
    st.sidebar.header("🧑‍🎓 Enter Student Details")
    name = st.sidebar.text_input("Student Name", "Aarav")
    study = st.sidebar.slider("Study Hours per Day", 0.0, 6.0, 2.0, 0.1)
    attend = st.sidebar.slider("Attendance (%)", 40, 100, 75)
    assign = st.sidebar.slider("Assignment Score", 0, 100, 60)

    input_data = pd.DataFrame([[study, attend, assign]],
        columns=["Study_Hours", "Attendance", "Assignment_Score"])

    result = model.predict(input_data)[0]
    label = "✅ Pass" if result == 1 else "❌ Fail"

    st.subheader("📢 Prediction Result")
    st.write(f"**Student Name:** {name}")
    st.write(f"**Study Hours:** {study} hrs/day")
    st.write(f"**Attendance:** {attend}%")
    st.write(f"**Assignment Score:** {assign}/100")
    st.markdown(f"### 🎯 **Prediction:** {label}")

# 6. Multiple Students Mode
else:
    st.markdown("### 🧑‍🤝‍🧑 Enter Multiple Students Below")

    # Example dataframe to edit
    sample_data = pd.DataFrame({
        "Name": ["Aarav", "Priya", "Rohit"],
        "Study_Hours": [2.5, 4.0, 3.8],
        "Attendance": [80, 65, 90],
        "Assignment_Score": [70, 50, 60]
    })

    edited_df = st.data_editor(sample_data, num_rows="dynamic", use_container_width=True)

    # Make prediction if there’s data
    if not edited_df.empty:
        features = edited_df[["Study_Hours", "Attendance", "Assignment_Score"]]
        preds = model.predict(features)
        edited_df["Prediction"] = ["✅ Pass" if p == 1 else "❌ Fail" for p in preds]

        st.subheader("📊 Prediction Results")
        st.dataframe(edited_df.reset_index(drop=True), use_container_width=True)

        # Optional: Download as CSV
        csv = edited_df.to_csv(index=False)
        st.download_button("⬇️ Download Results as CSV", csv, file_name="student_predictions.csv", mime="text/csv")
