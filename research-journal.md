# Research Journal: NeuroMark Pro 10x

## [2024-05-20] - Initial Deep Dive into TRIBE v2 Integration
- **Objective:** Understand how TRIBE v2 maps to marketing KPIs.
- **Findings:** TRIBE v2 predicts activation across 20,484 vertices on the fsaverage5 surface. Mapping these to the Destrieux Atlas allows us to isolate specific ROIs like the G_orbital for reward and G_front_sup for attention.
- **Hypothesis:** By weighting these activations, we can create a deterministic "Winning Probability" score that correlates with real-world CTR.
- **Constraints:** TRIBE v2 is a population-level model; individual variance is not captured, but it's highly effective for aggregate marketing trends.

## [2024-05-20] - Agent-as-a-Service (AaaS) Framework
- **Objective:** Design a multi-agent system that translates neuro-data into strategy.
- **System Design:** Using Gemini 2.0 Flash as the reasoning engine. Agents are given specific roles (Analyst, Strategist, etc.) to prevent context dilution and improve the quality of marketing advice.
