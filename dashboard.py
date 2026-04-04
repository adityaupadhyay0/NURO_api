import streamlit as st
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Pro SaaS Configuration
API_URL = "http://localhost:8000"
st.set_page_config(page_title="NeuroMark Pro SaaS", layout="wide", initial_sidebar_state="expanded")

# UI Styling
st.markdown("""
    <style>
    .main { background-color: #f7f9fc; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .ai-card { background-color: #f0f9ff; padding: 25px; border-radius: 15px; border-left: 6px solid #0284c7; margin: 15px 0; font-size: 1.1em; color: #0c4a6e; }
    .stTabs [data-baseweb="tab-list"] { gap: 30px; border-bottom: 2px solid #e2e8f0; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: 700; height: 60px; }
    </style>
    """, unsafe_allow_html=True)

# Application Sidebar (Workspace & Context)
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/000000/brain.png")
    st.title("NeuroMark Pro")
    campaign_name = st.text_input("Active Project", "Default Campaign")
    st.divider()

    st.subheader("📚 Project History")
    try:
        campaigns = requests.get(f"{API_URL}/campaigns").json()
        for c in campaigns:
            if st.button(f"📁 {c['name']} ({c['task_count']})"):
                st.session_state.active_campaign = c['name']
    except:
        st.info("Start your first project.")

# Application Navigation
st.title("🧠 Neuromarketing Dashboard")
tab1, tab2, tab3 = st.tabs(["🚀 Analysis", "📊 Strategic Insights", "🎓 Student Focus"])

with tab1:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Upload Creative")
        st.markdown("Supported: Video (mp4), Audio (wav/mp3), Text, URLs.")
        m_type = st.selectbox("Type", ["video", "audio", "text", "url"])

        uploaded_file = None
        text_input = None

        if m_type in ["video", "audio"]:
            uploaded_file = st.file_uploader(f"Choose {m_type}", type=["mp4", "wav", "mp3"])
        else:
            text_input = st.text_area("Input Content or URL")

        if st.button("🚀 Run Neuro-AI Analysis", type="primary"):
            files = None
            params = {"media_type": m_type, "campaign_name": campaign_name}
            if uploaded_file: files = {"file": uploaded_file.getvalue()}
            if text_input: params["text_content"] = text_input

            with st.spinner("Decoding Neural Signals..."):
                try:
                    response = requests.post(f"{API_URL}/analyze", params=params, files=files)
                    if response.status_code == 200:
                        st.session_state.task_id = response.json()["task_id"]
                        st.success(f"Task ID: {st.session_state.task_id}")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"API Connection Failed: {e}")

    with col2:
        if "task_id" in st.session_state:
            task_id = st.session_state.task_id
            try:
                res = requests.get(f"{API_URL}/results/{task_id}").json()
                if res["status"] == "processing":
                    st.info("🧠 Brain is thinking... (fsaverage5 simulation)")
                    st.progress(0.7)
                    time.sleep(3)
                    st.rerun()
                elif res["status"] == "completed":
                    data = res["data"]
                    df = pd.DataFrame(data["metrics"])
                    df["timestamp"] = data["timestamps"]

                    st.subheader("📊 Performance Summary")
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("Purchase Reward", f"{df['Reward'].mean():.1f}%")
                    k2.metric("Attention Hold", f"{df['Attention'].mean():.1f}%")
                    k3.metric("Emotional Peak", f"{df['Emotion'].max():.1f}%")
                    k4.metric("Cognitive Friction", f"{df['CognitiveLoad'].mean():.1f}%")

                    st.markdown("#### Neural Timeline")
                    st.line_chart(df.set_index("timestamp"))

                    with st.expander("🔍 MOMENT-OF-IMPACT (MOI) PEAKS"):
                        for peak in data.get("moi_analysis", []):
                            st.write(f"🔹 **{peak['type']}** at {peak['timestamp']:.1f}s (Value: {peak['value']:.1f}%)")

                    st.session_state.active_results = res
                else:
                    st.error(f"Analysis Failed: {res.get('error')}")
            except:
                st.info("Loading results...")
        else:
            st.info("Upload content to unlock neurological insights.")

with tab2:
    st.header("🧠 AI Strategic Consulting (Gemini)")
    if "active_results" in st.session_state:
        results_obj = st.session_state.active_results

        st.markdown(f'<div class="ai-card">{results_obj.get("ai_advice", "Analyzing neuro-correlations...")}</div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("💬 Ask Gemini About This Data")
        if "chat" not in st.session_state: st.session_state.chat = []
        for m in st.session_state.chat:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("How do I improve the Reward signal in the middle?"):
            st.session_state.chat.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.spinner("Gemini is interpreting..."):
                chat_res = requests.post(f"{API_URL}/chat/{results_obj['task_id']}", params={"query": prompt}).json()
                st.session_state.chat.append({"role": "assistant", "content": chat_res["response"]})
                with st.chat_message("assistant"): st.markdown(chat_res["response"])
    else:
        st.info("Run an analysis first to unlock AI consulting.")

with tab3:
    st.header("🎓 Student Focus Dashboard")
    if "active_results" in st.session_state:
        df = pd.DataFrame(st.session_state.active_results["data"]["metrics"])
        # Student Focus Index = Attention / Cognitive Load ratio
        focus_score = (df['Attention'].mean() / df['CognitiveLoad'].mean()) * 10

        c1, c2, c3 = st.columns(3)
        c1.metric("Student Focus Index", f"{focus_score:.1f}/10")
        c2.metric("Concept Retention", f"{df['Memory'].mean():.1f}%")
        c3.metric("Engagement Stability", f"{df['Attention'].std():.1f}")

        st.subheader("Engagement Heatmap")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df['Attention'], label='Focus (Attention)', color='teal')
        ax.fill_between(range(len(df)), df['CognitiveLoad'], alpha=0.2, label='Friction (Cognitive Load)', color='red')
        ax.legend()
        st.pyplot(fig)

        st.markdown(f'<div class="ai-card">📚 <b>Edu-Insight (AI):</b> Based on your data, your content has a Focus Index of {focus_score:.1f}. Try reducing complexity during spikes in Cognitive Load to increase retention.</div>', unsafe_allow_html=True)
    else:
        st.info("Upload educational content to view student analytics.")
