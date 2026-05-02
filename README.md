# 🧠 NeuroMark Pro 10x
### *The World's Most Advanced AI-Powered Brain Intelligence for Performance Marketers*

[![AaaS Architecture](https://img.shields.io/badge/Architecture-Agent--as--a--Service-blueviolet)](ARCHITECTURE.md)
[![Powered by TRIBE v2](https://img.shields.io/badge/Neuro--Engine-TRIBE%20v2-orange)](https://github.com/facebookresearch/tribev2)
[![Built with Gemini](https://img.shields.io/badge/Intelligence-Gemini%202.0%20Flash-blue)](https://deepmind.google/technologies/gemini/)

**NeuroMark Pro 10x** transforms the "guesswork" of performance marketing into a deterministic science. By combining **facebook/tribev2** fMRI-based foundation models with a **Multi-Agent Orchestration Brain**, we predict how your audience’s brains will react to ads *before* you spend a single dollar on traffic.

---

## 🚀 Why 10x?

Traditional A/B testing is slow and expensive. NeuroMark Pro provides:
- **Instant Winning Probability:** Know which ad will win the auction in seconds.
- **Agent-as-a-Service (AaaS):** Specialized AI agents (Creative Director, Media Buyer, Neuro-Scientist) collaborate to optimize your strategy.
- **Audience-Aware Weighting:** Deterministic calibration for specific ages, platforms (TikTok vs. Meta), and awareness levels.
- **10x Metrics:** Go beyond clicks to track *Scroll-Stop Rate*, *Purchase Intent*, *Creative Fatigue*, and *Visual Heatmaps*.

---

## 🛠 Core Features

### 🤖 The Neuro-Agent Command Center
A conversational "Brain" where you state your marketing goal (e.g., *"Beat my competitor in the luxury skincare niche"*). Our agents collaborate to:
- **Neuro-Analyst:** Identifies attention gaps in your creative.
- **Creative Strategist:** Writes high-ROAS hooks and scripts.
- **Media Buyer:** Optimizes your funnel and estimates auction CPMs.
- **CRO Optimizer:** Scrapes landing pages to eliminate conversion friction.

### 📊 Performance Marketing Intelligence
- **Batch Creative Ranking:** Upload up to 100 ads and get a ranked leaderboard of winning probability.
- **Competitor Neuro-Spy:** Analyze competitor URLs to extract their emotional "Secret Sauce."
- **Visual Attention Heatmaps:** See exactly where the eye goes during the peak engagement moment.
- **Creative Fatigue Forecasting:** Predict the "shelf life" of your ad based on neural saturation.
- **Reality Feedback Loop:** Input real CTR/CPA data to calibrate the model’s predictions to your specific account.

---

## 🏗 Modular "10x" Architecture

- **`/core`**: The power-house. Contains the `NeuroEngine` (TRIBE v2 integration) and the SQLAlchemy Database layer.
- **`/agents`**: specialized Gemini-powered agents with distinct roles, goals, and backstories.
- **`/services`**: The `BrainOrchestrator` that manages multi-agent collaboration.
- **`/interface`**: A unified Streamlit Dashboard for command and control.

---

## ⚡ Quick Start

### 1. Requirements
- Python 3.10+
- GPU (Optional but recommended for TRIBE v2 inference)
- [Gemini API Key](https://aistudio.google.com/app/apikey)

### 2. Installation
```bash
# Clone the repo
git clone https://github.com/your-repo/neuromark-pro-10x.git
cd neuromark-pro-10x

# Install TRIBE v2 directly from Facebook Research
pip install git+https://github.com/facebookresearch/tribev2.git

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root:
```env
GEMINI_API_KEY=your_key_here
```

### 4. Launch the Command Center
```bash
# Start the Backend API
python app.py &

# Launch the Dashboard
streamlit run interface/dashboard.py
```

---

## 🗺 Roadmap to Global Dominance
See [ROADMAP.md](ROADMAP.md) for our path from **MMP** to **Post-Human Creative Ecosystems**.

---

## 🤝 Contributing
We are building the future of programmable advertising. If you are a neuroscientist, performance marketer, or AI engineer, we want your input.

---
*Disclaimer: NeuroMark Pro 10x uses fMRI-trained foundation models to simulate population-level brain responses. It is intended for marketing optimization and educational insights.*
