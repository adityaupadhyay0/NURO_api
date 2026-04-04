import torch
import numpy as np
import pandas as pd
from tribev2 import TribeModel
from nilearn import datasets
import os
import uuid

class NeuroEngine:
    def __init__(self, model_id="facebook/tribev2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initializing NeuroEngine on {self.device}...")
        self.model = TribeModel.from_pretrained(model_id)
        # Note: model.to() might not be supported if it's a wrapper,
        # but TribeModel handles its internal torch modules.

        # Load Destrieux Atlas on fsaverage5 surface (standard for TRIBE v2)
        # fsaverage5 has 10,242 vertices per hemisphere.
        self.destrieux = datasets.fetch_atlas_surf_destrieux()
        self.left_atlas = self.destrieux['map_left']   # shape (10242,)
        self.right_atlas = self.destrieux['map_right'] # shape (10242,)

        # Marketing ROI Mapping (indices from Destrieux)
        # 16: G_front_sup, 55: S_front_sup, 15: G_front_middle, 54: S_front_middle
        # 18: G_insular_short, 6: G_and_S_cingul-Ant, 7: G_and_S_cingul-Mid-Ant
        # 24: G_orbital, 65: S_orbital-H_Shaped, 31: G_rectus, 32: G_subcallosal
        # 23: G_oc-temp_med-Parahip, 62: S_oc-temp_med_and_Lingual
        # 2: G_and_S_occipital_inf, 11: G_cuneus, 45: S_calcarine
        self.roi_map = {
            "Attention": [16, 55, 15, 54],
            "Emotion": [18, 6, 7],
            "Reward": [24, 65, 31, 32],
            "Memory": [23, 62],
            "CognitiveLoad": [54, 4],
            "VisualEngagement": [2, 11, 45]
        }

    def analyze_media(self, file_path, media_type="video"):
        print(f"Analyzing {media_type}: {file_path}")

        if media_type == "video":
            df_events = self.model.get_events_dataframe(video_path=file_path)
        elif media_type == "audio":
            df_events = self.model.get_events_dataframe(audio_path=file_path)
        elif media_type == "text":
            df_events = self.model.get_events_dataframe(text_path=file_path)
        elif media_type == "url":
            import requests
            from bs4 import BeautifulSoup
            # Fix Race Condition: Unique temp file per request
            u_id = str(uuid.uuid4())
            temp_path = f"uploads/{u_id}_url.txt"
            try:
                page = requests.get(file_path, timeout=10)
                soup = BeautifulSoup(page.content, 'html.parser')
                text = ' '.join([p.get_text() for p in soup.find_all('p')])
                with open(temp_path, "w") as f:
                    f.write(text)
                df_events = self.model.get_events_dataframe(text_path=temp_path)
            except Exception as e:
                if os.path.exists(temp_path): os.remove(temp_path)
                raise e
        else:
            raise ValueError(f"Unsupported media type: {media_type}")

        preds, segments = self.model.predict(events=df_events)
        # TRIBE v2 predicts on fsaverage5: (n_timesteps, 20484)
        # where the first 10242 vertices are Left Hem, and next 10242 are Right Hem.

        return self._process_predictions(preds, segments)

    def _process_predictions(self, preds, segments):
        if isinstance(preds, torch.Tensor):
            preds = preds.detach().cpu().numpy()

        n_lh = 10242
        results = {
            "timestamps": segments["onset"].tolist(),
            "metrics": {}
        }

        # Scientific ROI extraction across both hemispheres
        for metric_name, indices in self.roi_map.items():
            lh_mask = np.isin(self.left_atlas, indices)
            rh_mask = np.isin(self.right_atlas, indices)

            # Combine to full-brain mask (20484 vertices)
            full_mask = np.concatenate([lh_mask, rh_mask])

            # Ensure mask alignment
            if full_mask.shape[0] != preds.shape[1]:
                # Fallback if model output shape differs (should not on fsaverage5)
                full_mask = full_mask[:preds.shape[1]]

            # Mean activation for the metric
            metric_series = preds[:, full_mask].mean(axis=1)
            results["metrics"][metric_name] = self._normalize(metric_series).tolist()

        # Spatial Peak for 3D mapping
        peak_idx = results["metrics"]["Attention"].index(max(results["metrics"]["Attention"]))
        results["spatial_peak"] = preds[peak_idx].tolist()

        # MOI Analysis
        moi_events = []
        emotion_vals = results["metrics"]["Emotion"]
        for i in range(1, len(emotion_vals) - 1):
            if emotion_vals[i] > 80 and emotion_vals[i] > emotion_vals[i-1]:
                moi_events.append({
                    "timestamp": results["timestamps"][i],
                    "type": "Emotional Peak",
                    "value": emotion_vals[i]
                })
        results["moi_analysis"] = sorted(moi_events, key=lambda x: x['value'], reverse=True)[:5]

        return results

    def _normalize(self, series):
        s_min, s_max = series.min(), series.max()
        if s_max - s_min == 0:
            return series * 0
        return ((series - s_min) / (s_max - s_min)) * 100
