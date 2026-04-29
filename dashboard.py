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
st.title("🧠 Performance Marketing Neuro-Predictor")
tab1, tab2, tab3 = st.tabs(["🚀 Predict & Optimize", "📊 Creative Strategy", "📉 Prediction vs. Reality"])

with tab1:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("1. Define Target Audience")
        age = st.selectbox("Age Range", ["18-24", "25-34", "35-44", "45-54", "55+"])
        platform = st.selectbox("Platform", ["Meta", "TikTok", "YouTube", "LinkedIn", "Google Display"])
        industry = st.selectbox("Industry", ["D2C", "SaaS", "Info Products", "Professional Services"])
        awareness = st.selectbox("Awareness Level", ["Cold", "Warm", "Hot"])

        st.divider()
        st.header("2. Upload Creative")
        m_type = st.selectbox("Media Type", ["video", "audio", "text", "url"])

        uploaded_file = None
        text_input = None

        if m_type in ["video", "audio"]:
            uploaded_file = st.file_uploader(f"Choose {m_type}", type=["mp4", "wav", "mp3"])
        else:
            text_input = st.text_area("Input Content or URL")

        if st.button("🚀 Predict Winning Probability", type="primary"):
            files = None
            params = {
                "media_type": m_type,
                "campaign_name": campaign_name,
                "age": age,
                "platform": platform,
                "industry": industry,
                "awareness": awareness
            }
            if uploaded_file: files = {"file": uploaded_file.getvalue()}
            if text_input: params["text_content"] = text_input

            with st.spinner("Simulating Audience Response..."):
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
                    df = pd.DataFrame(data["marketing_kpis"])
                    df["timestamp"] = data["timestamps"]

                    st.subheader("🎯 Predictive Performance Summary")
                    k1, k2, k3, k4 = st.columns(4)

                    # Winning Probability Large Gauge
                    win_prob = data.get("winning_probability", 0)
                    st.metric("Winning Probability", f"{win_prob:.1f}%", help="Likelihood of this ad outperforming the platform average.")

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Scroll-Stop Rate", f"{df['ScrollStopRate'].mean():.1f}%")
                    c2.metric("Purchase Intent", f"{df['PurchaseIntent'].mean():.1f}%")
                    c3.metric("Clarity Score", f"{df['Clarity'].mean():.1f}%")
                    c4.metric("Brand Recall", f"{df['BrandRecall'].mean():.1f}%")

                    st.markdown("#### Predictive KPI Timeline")
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
    st.header("🧠 Creative Optimization Strategy")
    if "active_results" in st.session_state:
        results_obj = st.session_state.active_results

        st.markdown(f'<div class="ai-card">{results_obj.get("ai_advice", "Analyzing neuro-correlations...")}</div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("💬 Ask Your Creative Strategist")
        if "chat" not in st.session_state: st.session_state.chat = []
        for m in st.session_state.chat:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("How do I improve the Scroll-Stop rate?"):
            st.session_state.chat.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.spinner("Gemini is interpreting..."):
                chat_res = requests.post(f"{API_URL}/chat/{results_obj['task_id']}", params={"query": prompt}).json()
                st.session_state.chat.append({"role": "assistant", "content": chat_res["response"]})
                with st.chat_message("assistant"): st.markdown(chat_res["response"])
    else:
        st.info("Run a prediction first to unlock creative strategy.")

with tab3:
    st.header("📉 Feedback Loop: Reality vs. Prediction")
    if "active_results" in st.session_state:
        res_obj = st.session_state.active_results

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("1. Enter Real Performance")
            with st.form("market_results"):
                ctr = st.number_input("Real CTR (%)", min_value=0.0, max_value=100.0, step=0.1)
                cpa = st.number_input("Real CPA ($)", min_value=0.0, step=0.01)
                notes = st.text_area("Campaign Notes")
                submit = st.form_submit_button("Save Results")

                if submit:
                    payload = {"task_id": res_obj["task_id"], "ctr": ctr, "cpa": cpa, "notes": notes}
                    resp = requests.post(f"{API_URL}/submit_results", json=payload)
                    if resp.status_code == 200:
                        st.success("Results saved! The system is learning.")
                    else:
                        st.error("Failed to save results.")

        with col_b:
            st.subheader("2. Performance Calibration")
            actuals = res_obj.get("marketing_actuals")
            if actuals and actuals.get("ctr"):
                predicted_ctr = np.mean(res_obj["data"]["marketing_kpis"]["ScrollStopRate"]) / 20 # Rough scaling
                diff = actuals["ctr"] - predicted_ctr

                st.metric("Prediction Variance (CTR)", f"{diff:+.2f}%")
                if abs(diff) < 0.5:
                    st.success("Prediction was HIGHLY ACCURATE.")
                else:
                    st.warning("Prediction vs Reality Gap detected. Gemini is analyzing...")
            else:
                st.info("Enter market data to see calibration.")
    else:
        st.info("Predict a creative first.")
