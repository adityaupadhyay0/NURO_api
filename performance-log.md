# Performance Log: NeuroMark Pro 10x

## [2024-05-20] - Baseline Inference Assessment
- **Environment:** CPU-based (standard sandbox environment).
- **Metric:** Inference Latency.
- **Observation:** Inference for a 30s video takes approximately 45-60 seconds on CPU.
- **Optimization Target:** Move to batch inference and implement better caching for embedding reuse.

## [2024-05-20] - Queue Latency
- **Observation:** Background tasks in FastAPI handle concurrency well, but the `threading.Lock` in `NeuroEngine` ensures sequential processing of heavy model calls to prevent memory overflow.
