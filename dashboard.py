import streamlit as st
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(page_title="NeuroMark SaaS", layout="wide")

st.title("🧠 NeuroMark SaaS: Marketing Insights Dashboard")
st.markdown("Analyze consumer brain responses to your video, audio, and text content using TRIBE v2.")

# Tabs for different analysis modes
tab1, tab2 = st.tabs(["Analyze Content", "A/B Comparison"])

with tab1:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Upload Media")
        media_type = st.selectbox("Media Type", ["video", "audio", "text"])

        uploaded_file = None
        text_input = None

        if media_type in ["video", "audio"]:
            uploaded_file = st.file_uploader(f"Choose a {media_type} file...", type=["mp4", "wav", "mp3"])
        else:
            text_input = st.text_area("Paste news article/ad copy here:")

        if st.button("Run Neuro-Analysis"):
            if uploaded_file or text_input:
                with st.spinner("Submitting task to TRIBE v2 engine..."):
                    files = None
                    if uploaded_file:
                        files = {"file": uploaded_file.getvalue()}

                    data = {"media_type": media_type}
                    if text_input:
                        data["text_content"] = text_input

                    response = requests.post(f"{API_URL}/analyze", params=data)

                    if response.status_code == 200:
                        task_id = response.json()["task_id"]
                        st.success(f"Task Started! ID: {task_id}")
                        st.session_state.task_id = task_id
                    else:
                        st.error("Failed to start task.")
            else:
                st.warning("Please provide media.")

    with col2:
        st.header("Results & Insights")
        if "task_id" in st.session_state:
            task_id = st.session_state.task_id
            status_container = st.empty()

            # Polling for results
            while True:
                response = requests.get(f"{API_URL}/results/{task_id}")
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")

                    if status == "processing":
                        status_container.info("🧠 Brain is thinking... (Processing with TRIBE v2)")
                        time.sleep(5)
                    elif status == "completed":
                        status_container.success("Analysis Complete!")
                        results = data["data"]

                        # Prepare data for plotting
                        df = pd.DataFrame(results["metrics"])
                        df["timestamp"] = results["timestamps"]

                        # Summary Metrics
                        st.subheader("Key Performance Indicators")
                        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                        kpi1.metric("Avg Attention", f"{df['Attention'].mean():.1f}%")
                        kpi2.metric("Emotional Peak", f"{df['Emotion'].max():.1f}%")
                        kpi3.metric("Reward Signal", f"{df['Reward'].mean():.1f}%")
                        kpi4.metric("Cognitive Friction", f"{df['CognitiveLoad'].mean():.1f}%")

                        # Main Plot
                        st.subheader("Neuro-Response Timeline")
                        fig, ax = plt.subplots(figsize=(12, 6))
                        for col in results["metrics"].keys():
                            ax.plot(df["timestamp"], df[col], label=col, alpha=0.8, linewidth=2)
                        ax.set_xlabel("Time (seconds)")
                        ax.set_ylabel("Neural Activation (%)")
                        ax.legend()
                        st.pyplot(fig)

                        # Actionable Insight
                        st.subheader("Actionable Recommendations")
                        if df['Reward'].mean() < 50:
                            st.info("💡 Insight: The 'Reward' signal is low. Consider adding more aspirational or gratifying imagery.")
                        if df['CognitiveLoad'].max() > 80:
                            st.warning("⚠️ Warning: High 'Cognitive Friction' detected at specific segments. Simplify the messaging.")

                        break
                    elif status == "failed":
                        status_container.error(f"Analysis Failed: {data.get('error')}")
                        break
                else:
                    st.error("Error fetching results.")
                    break
        else:
            st.info("Upload content to see neuro-insights.")

with tab2:
    st.header("A/B Performance Comparison")
    st.markdown("Compare two versions of your marketing material to see which one triggers more brand desire.")
    # (Simplified for MVP, would involve selecting two completed task IDs)
    st.info("Feature Coming Soon: Select two completed analyses to view head-to-head metrics.")
