# Production Architecture: NeuroMark SaaS

## Overview
A production-ready SaaS for neuro-marketing insights leveraging the TRIBE v2 foundation model.

## Component Stack
- **AI Engine**: TRIBE v2 (facebookresearch) for tri-modal brain response prediction.
- **Backend API**: FastAPI (high performance, asynchronous).
- **Worker**: Background tasks for heavy inference.
- **Database**: SQLite (for MVP/Production-ready local state) or PostgreSQL.
- **Frontend**: Streamlit-based Marketing Dashboard.
- **Processing**: Nilearn for brain atlas mapping and ROI extraction.

## Data Flow
1. User uploads Media (Video/Audio/Text) via Dashboard.
2. FastAPI receives the request, stores the file, and triggers an Inference Task.
3. `NeuroEngine` runs TRIBE v2 on the media to get vertex-level brain activations.
4. `AnalyticsService` maps vertices to Destrieux ROIs (Attention, Reward, Emotion, Memory).
5. Results are aggregated into time-series data and stored.
6. Dashboard fetches results and displays:
   - Emotional Heatmap over time.
   - Brand Desire Score (Reward ROI).
   - Story Retention Probablity (Memory ROI).
   - Comparison between multiple ad versions.

## Neuro-Marketing ROI Mapping (Destrieux Atlas)
- **Attention (Focus)**: `G_front_sup` (16), `S_front_sup` (55) - Prefrontal areas associated with sustained attention.
- **Emotional Valence (Engagement)**: `G_insular_short` (18), `G_and_S_cingul-Ant` (6) - Limbic associated regions.
- **Reward/Value (Desire)**: `G_orbital` (24), `S_orbital-H_Shaped` (65) - Orbitofrontal cortex, key for valuation.
- **Memory Encoding (Impact)**: `G_oc-temp_med-Parahip` (23) - Parahippocampal gyrus for episodic memory.
- **Cognitive Load (Friction)**: `S_front_middle` (54) - Dorsolateral prefrontal cortex.
