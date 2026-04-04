import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(page_title="EduEngage - Student Focus Dashboard", layout="wide")

st.title("🎓 EduEngage: Student Engagement Analytics")
st.markdown("Optimize your educational content for maximum student retention and focus.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Upload Lecture/Educational Content")
    media_type = st.selectbox("Content Type", ["video", "audio", "text"])

    uploaded_file = st.file_uploader(f"Choose a {media_type} file...", type=["mp4", "wav", "mp3", "pdf", "txt"])

    if st.button("Generate Engagement Score"):
        if uploaded_file:
            with st.spinner("Analyzing neural engagement signals..."):
                # Simplified for demo: in production would use the same backend /analyze endpoint
                data = {"media_type": media_type}
                response = requests.post(f"{API_URL}/analyze", params=data)

                if response.status_code == 200:
                    task_id = response.json()["task_id"]
                    st.success(f"Edu-Task Started! ID: {task_id}")
                    st.session_state.edu_task_id = task_id
                else:
                    st.error("Failed to start analysis.")
        else:
            st.warning("Please upload content.")

with col2:
    st.header("Student Engagement Dashboard")
    if "edu_task_id" in st.session_state:
        task_id = st.session_state.edu_task_id
        response = requests.get(f"{API_URL}/results/{task_id}")

        if response.status_code == 200:
            data = response.json()
            if data["status"] == "completed":
                results = data["data"]
                df = pd.DataFrame(results["metrics"])

                # Educational ROI: Focus & Cognitive Load
                st.subheader("Engagement Index")
                # Focus Score is Attention / Cognitive Load ratio
                focus_score = (df['Attention'].mean() / df['CognitiveLoad'].mean()) * 10

                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Student Focus Score", f"{focus_score:.1f}/10")
                kpi2.metric("Story Retention", f"{df['Memory'].mean():.1f}%")
                kpi3.metric("Engagement Stability", f"{df['Attention'].std():.1f}")

                # Plot focus over time
                st.subheader("Engagement Over Time")
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(results["timestamps"], df['Attention'], label='Attention (Focus)', color='green')
                ax.fill_between(results["timestamps"], df['CognitiveLoad'], alpha=0.3, label='Cognitive Load', color='red')
                ax.legend()
                st.pyplot(fig)

                # Educational Insights
                st.info("📚 Educational Insight: Your student's focus peaks during segments with high 'Attention' and low 'Cognitive Load'. Consider breaking the lesson at points where cognitive load spikes.")
            else:
                st.info(f"Task {task_id} is {data['status']}...")
    else:
        st.info("Upload educational content to see engagement analytics.")
