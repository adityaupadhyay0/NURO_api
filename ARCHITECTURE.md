# 🏗 10x Architecture: Agent-as-a-Service (AaaS)

NeuroMark Pro 10x is built on a modular, multi-layered architecture designed for high-throughput performance marketing analysis and assistive AI decision-making.

---

## 1. System Layers

### 🧠 Core Engine (`/core`)
- **`neuro_engine.py`**: The "Heart." Integrates `facebook/tribev2` to simulate brain responses across 20,484 vertices. It handles trilateral media processing (Video, Audio, Text/URL) and maps neural signals to the Destrieux Surface Atlas.
- **`database.py`**: The "Memory." SQLAlchemy-based persistence layer for Campaigns, Analysis Tasks, and Marketing Results.

### 🤖 Multi-Agent Layer (`/agents`)
Our "Brain" is not a single LLM, but a collaborative ecosystem of specialized agents built on **Gemini 2.0 Flash**:
- **Neuro-Analyst**: Specializes in scientific data interpretation and bottleneck detection.
- **Creative Strategist**: Expert in D2C hooks, psychological triggers, and ad copy.
- **Media Buyer**: Focused on auction dynamics, CPM estimation, and funnel logic.
- **CRO Optimizer**: Conversion rate specialist for landing page and CTA refinement.

### ⚙️ Orchestration Layer (`/services`)
- **`brain_orchestrator.py`**: The "Conductor." Coordinates communication between agents and ensures that raw neuro-data is translated into actionable marketing strategy.

### 🖥 Interface Layer (`/interface`)
- **`dashboard.py`**: The "Cockpit." A unified Streamlit interface that provides 7+ modules for marketing execution, from Batch Ranking to "Competitor Spy" analysis.

---

## 2. The 10x Transformation Logic

We apply a proprietary **Deterministic Calibration** layer between the raw scientific data and the user-facing KPIs:

1. **Neural Inference**: TRIBE v2 predicts fMRI-level activation.
2. **ROI Mapping**: Activation is mapped to 6 core Neuro-ROIs (Attention, Reward, etc.).
3. **Marketing KPI Calculation**:
   - *Scroll-Stop Rate* = Attention (70%) + Visual Engagement (30%)
   - *Purchase Intent* = Reward (60%) + Emotion (40%) - Friction (20%)
4. **Audience-Aware Weighting**: KPIs are adjusted based on:
   - **Platform Context**: (e.g., TikTok requires higher hooks but offers higher virality).
   - **Audience Age**: (e.g., Gen Z has higher cognitive friction for traditional "salesy" ads).
   - **Industry Benchmarks**: Psychographic multipliers for SaaS, D2C, and Info-Products.

---

## 3. High-Throughput Design
- **GPU Concurrency**: The `NeuroEngine` uses `threading.Lock` to ensure the foundation model handles batch requests without race conditions.
- **Asynchronous Background Tasks**: FastAPI processes heavy neural simulations in the background, allowing the UI to remain responsive.

---

## 4. Feedback Loop: Machine Learning Calibration
The system includes a manual feedback loop where marketers input real-world results (CTR, CPA). This data is stored alongside the predictions, allowing the `Neuro-Analyst` agent to calibrate future strategy based on actual "Prediction vs. Reality" variances.
