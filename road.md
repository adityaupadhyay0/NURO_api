# Vision
NeuroMark Pro 10x aims to be the world’s most advanced AI-powered marketing intelligence platform, transforming creative intuition into measurable cognitive prediction.

# Current Product State
- MMP and Scale & Intelligence phases (Phase 1 & 2) are mostly completed.
- Core systems: NeuroEngine (TRIBE v2), Multi-Agent System (Gemini 2.0 Flash), Performance Marketing Intelligence, and Streamlit Interface.
- Support for video, audio, text, and URL analysis.

# Neuro Engine State
- Integrates `facebook/tribev2` for fMRI-based brain response simulation.
- Maps neural signals to 6 core marketing ROIs (Attention, Emotion, Reward, Memory, Cognitive Load, Visual Engagement).
- Implements audience-aware weighting (Deterministic Calibration).
- **Update (May 2026):** Added telemetry for GPU lock wait time and inference latency.

# Multi-Agent State
- AaaS model with specialized agents: Neuro-Analyst, Creative Strategist, Media Buyer, and CRO Optimizer.
- Coordinated by `CampaignBrain` service.
- **Update (May 2026):** Implemented prompt sanitization (regex-based, case-insensitive) for all agents.

# Current Architecture
- Modular "10x" architecture: `/core` (NeuroEngine, Database), `/agents` (Specialized agents), `/services` (Brain Orchestrator), and `/interface` (Streamlit Dashboard).
- FastAPI backend with asynchronous background tasks for inference.

# Infrastructure State
- SQLite database for persistence.
- Local filesystem for file uploads.
- threading.Lock used for GPU concurrency control in TRIBE v2.
- **Update (May 2026):** Secured file ingestion with `secure_filename`.

# Performance State
- Inference is performed in the background to maintain UI responsiveness.
- Multi-threaded batch analysis implemented.
- Real-time telemetry now tracking core engine latency.

# Security State
- Hardened: Implemented prompt injection mitigation, secure file upload handling, and API rate limiting.
- Completed: API authentication and RBAC.

# UX State
- Streamlit dashboard providing 7+ modules for marketing execution.
- Includes "Creative Battle Royale", "Batch Ranking", and "Competitor Spy".

# Scientific Limitations
- Based on simulated population-level brain responses (TRIBE v2).
- Accuracy depends on the alignment of training data with real-world marketing contexts.

# AI Reliability State
- Uses Gemini 2.0 Flash for agents.
- Hallucination risks exist in non-deterministic agent reasoning.
- Improved robustness through input sanitization.

# Current Repository Health
- Modular and organized.
- Automated tests (pytest) are active and passing (10/10).

# Technical Debt
- Need for more granular telemetry in agent orchestration.

# Active Task
- Optimizing NeuroEngine inference latency and caching.

# Queued Tasks
1. Optimizing inference latency.
4. Synthetic audience simulation expansion.
5. Neuro-native generation integration.
6. Global performance benchmarks implementation.

# Research Integrations
- TRIBE v2 foundation model.
- Gemini 2.0 Flash AaaS framework.
- Destrieux Surface Atlas for ROI mapping.

# Recently Completed Tasks
- API Rate Limiting: Implemented using `slowapi` to protect sensitive endpoints from abuse and resource exhaustion.
- API Authentication & RBAC: Implemented JWT-based auth and role-based permissions (Admin, Marketer, Viewer).
- Security Hardening: Implemented prompt sanitization and secure file handling.
- Observability: Added performance telemetry to the NeuroEngine.
- Environment: Stabilized test dependencies and verification suite.
- Multi-Agent Orchestration: Refactored CampaignBrain to use LLM-powered dynamic planning.

# Next 10 Priorities
1. API Authentication.
2. Rate Limiting.
3. Platform integrations (Meta/TikTok).
4. Synthetic personas training.
5. AI-driven creative generation.
6. Predictive culture shift engine.

# Next 100 Improvements
- [ ] BCI research bridge.
- [ ] Haptic/Spatial neuro-inference.

# Execution Log
## [2026-05-20]
### Completed
- Implemented API Rate Limiting for all sensitive endpoints using `slowapi`.
- Stabilized environment and test suite (fixed duplicate registrations and datetime deprecations).
- Environment stabilization (pip install dependencies).
- Verified current state with 10 passed tests.
- Implemented `BaseAgent._sanitize` for case-insensitive prompt injection mitigation.
- Integrated `secure_filename` in `app.py` for file upload security.
- Added performance metrics (latency tracking) to `NeuroEngine.analyze_media`.
- Updated `security-audit.md` and `road.md`.

### Discovered
- Basic `str.replace` for sanitization was case-sensitive; upgraded to regex for robustness.
- NeuroEngine lacked telemetry for identifying bottlenecks in the background task queue.

### Architecture Changes
- Added a metadata payload to analysis results for infrastructure telemetry.

### Reliability Findings
- Background tasks now more observable via timing logs.

### Security Findings
- Mitigated path traversal and basic prompt injection.
