import torch
import numpy as np
import pandas as pd
from tribev2 import TribeModel
from nilearn import datasets
import os

class NeuroEngine:
    def __init__(self, model_id="facebook/tribev2", device=None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"Initializing NeuroEngine...")
        self.model = TribeModel.from_pretrained(model_id)
        # The model might handle device internally or be a Pydantic object wrapping torch.

        # Load Atlas for ROI mapping
        self.destrieux = datasets.fetch_atlas_surf_destrieux()
        self.labels = self.destrieux['labels']
        self.left_atlas = self.destrieux['map_left']
        # Note: tribev2 predicts on fsaverage5 (~20k vertices).
        # Nilearn's destrieux surface atlas labels should match if resampled or if
        # the model output vertices are aligned with fsaverage5.

        # Marketing ROI Mapping (indices from research)
        self.roi_map = {
            "Attention": [16, 55],       # G_front_sup, S_front_sup
            "Emotion": [18, 6],          # G_insular_short, G_and_S_cingul-Ant
            "Reward": [24, 65],          # G_orbital, S_orbital-H_Shaped
            "Memory": [23],               # G_oc-temp_med-Parahip
            "CognitiveLoad": [54]        # S_front_middle
        }

    def analyze_media(self, file_path, media_type="video"):
        """
        Analyzes video, audio, or text file and returns marketing neuro-insights.
        """
        print(f"Analyzing {media_type}: {file_path}")

        if media_type == "video":
            df_events = self.model.get_events_dataframe(video_path=file_path)
        elif media_type == "audio":
            df_events = self.model.get_events_dataframe(audio_path=file_path)
        elif media_type == "text":
            # For text, TRIBE v2 converts to speech then analyzes
            df_events = self.model.get_events_dataframe(text_path=file_path)
        else:
            raise ValueError("Unsupported media type. Use 'video', 'audio', or 'text'.")

        preds, segments = self.model.predict(events=df_events)
        # preds shape: (n_timesteps, n_vertices)

        return self._process_predictions(preds, segments)

    def _process_predictions(self, preds, segments):
        """
        Maps vertex-level predictions to marketing ROIs.
        """
        n_timesteps = preds.shape[0]
        results = {
            "timestamps": segments["onset"].tolist(),
            "metrics": {}
        }

        for metric_name, indices in self.roi_map.items():
            # Combine vertices for all ROIs in this metric
            combined_mask = np.zeros(preds.shape[1], dtype=bool)
            for idx in indices:
                # We assume left hemisphere for simplicity in MVP,
                # or we could average both if the model provides them.
                # TRIBE v2 fsaverage5 is usually 10242 vertices per hemisphere.
                # preds often contains both (20484 vertices).
                mask = (self.left_atlas == idx)
                if len(mask) < preds.shape[1]:
                    # Pad mask for both hemispheres if needed
                    full_mask = np.zeros(preds.shape[1], dtype=bool)
                    full_mask[:len(mask)] = mask
                    # Optional: apply same mask to right hemisphere if symmetric
                    # (Simplified for now)
                    combined_mask |= full_mask
                else:
                    combined_mask |= mask[:preds.shape[1]]

            # Calculate mean activation for this ROI group over time
            metric_series = preds[:, combined_mask].mean(axis=1)
            # Normalize to 0-100 for business readability
            metric_series = self._normalize(metric_series)
            results["metrics"][metric_name] = metric_series.tolist()

        return results

    def _normalize(self, series):
        # Simple min-max scaling for UI presentation
        if isinstance(series, torch.Tensor):
            series = series.detach().cpu().numpy()
        s_min, s_max = series.min(), series.max()
        if s_max - s_min == 0:
            return series * 0
        return ((series - s_min) / (s_max - s_min)) * 100

if __name__ == "__main__":
    # Test initialization
    engine = NeuroEngine()
    print("NeuroEngine ready.")
