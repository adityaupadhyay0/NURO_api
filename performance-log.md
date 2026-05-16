# Performance Log: NeuroMark Pro 10x

## [2024-05-20] - Baseline Inference Assessment
- **Environment:** CPU-based (standard sandbox environment).
- **Metric:** Inference Latency.
- **Observation:** Inference for a 30s video takes approximately 45-60 seconds on CPU.
- **Optimization Target:** Move to batch inference and implement better caching for embedding reuse.

## [2024-05-20] - Queue Latency
- **Observation:** Background tasks in FastAPI handle concurrency well, but the `threading.Lock` in `NeuroEngine` ensures sequential processing of heavy model calls to prevent memory overflow.

## [2026-05-21] - Infrastructure Hardening
- **Feature:** API Rate Limiting.
- **Metric:** Overhead.
- **Observation:** Minimal latency added by `slowapi` middleware (<5ms). Protection against high-compute inference spikes is now active.
- **Optimization:** Refactored all internal time tracking to use UTC-aware objects for consistency across distributed inference workers.

## [2026-05-22] - Persistent Neural Caching
- **Feature:** Disk-based prediction caching (SHA-256).
- **Metric:** Cache Hit Latency vs. Inference Latency.
- **Observation:** Warm runs (cache hits) reduced latency from ~1s (mocked inference) to <0.01s.
- **Speedup:** ~170x gain on repeated creatives.
- **Optimization:** Integrated `torch.inference_mode()` for additional inference-time efficiency gains.
