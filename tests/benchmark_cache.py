import time
import os
import torch
import numpy as np
from unittest.mock import MagicMock, patch

# Mock TribeModel and Atlas before importing NeuroEngine
with patch('tribev2.TribeModel.from_pretrained') as mock_pretrained:
    with patch('nilearn.datasets.fetch_atlas_surf_destrieux') as mock_atlas:
        mock_atlas.return_value = {
            'map_left': np.zeros(10242, dtype=int),
            'map_right': np.zeros(10242, dtype=int)
        }
        from core.neuro_engine import NeuroEngine
        from core.config import CACHE_DIR

def run_benchmark():
    print("--- Starting NeuroEngine Cache Benchmark ---")

    # 1. Setup Mock Engine
    with patch('tribev2.TribeModel.from_pretrained') as mock_pretrained:
        mock_model = MagicMock()
        mock_pretrained.return_value = mock_model

        # Simulate heavy inference (1 second)
        def slow_predict(*args, **kwargs):
            time.sleep(1.0)
            preds = torch.rand(1, 20484)
            segments = {"onset": np.array([0.0])}
            return preds, segments

        mock_model.predict.side_effect = slow_predict
        mock_model.get_events_dataframe.return_value = MagicMock()

        engine = NeuroEngine()

    # 2. Create a dummy file
    dummy_path = "test_creative.txt"
    with open(dummy_path, "w") as f:
        f.write("This is a dummy creative for benchmarking.")

    # 3. Clear existing cache for this file if it exists
    from core.hashing import calculate_file_hash
    file_hash = calculate_file_hash(dummy_path)
    cache_path = os.path.join(CACHE_DIR, f"{file_hash}.pkl")
    if os.path.exists(cache_path):
        os.remove(cache_path)

    # 4. Cold Run (No Cache)
    print("\n[Cold Run] Analyzing media for the first time...")
    start_cold = time.time()
    results_cold = engine.analyze_media(dummy_path, media_type="text")
    duration_cold = time.time() - start_cold
    print(f"Cold Run Duration: {duration_cold:.4f}s")

    # 5. Warm Run (Cached)
    print("\n[Warm Run] Analyzing the same media again (should hit cache)...")
    start_warm = time.time()
    results_warm = engine.analyze_media(dummy_path, media_type="text")
    duration_warm = time.time() - start_warm
    print(f"Warm Run Duration: {duration_warm:.4f}s")

    # 6. Verification
    speedup = duration_cold / duration_warm
    print(f"\nSpeedup: {speedup:.2f}x")

    assert duration_warm < duration_cold, "Warm run should be faster than cold run"
    assert results_cold["winning_probability"] == results_warm["winning_probability"], "Results should be identical"

    print("\nBenchmark Success: Caching is working as expected.")

    # Cleanup
    if os.path.exists(dummy_path): os.remove(dummy_path)

if __name__ == "__main__":
    run_benchmark()
