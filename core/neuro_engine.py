import torch
import numpy as np
import pandas as pd
from tribev2 import TribeModel
from nilearn import datasets
import os
import uuid
import threading
import time
import logging
import pickle
from core.config import UPLOAD_DIR, TRIBE_MODEL_ID, CACHE_DIR
from core.hashing import calculate_file_hash

logger = logging.getLogger(__name__)

class NeuroEngine:
    def __init__(self, model_id=TRIBE_MODEL_ID):
        self.lock = threading.Lock()
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

    def analyze_media(self, file_path, media_type="video", audience_params=None):
        logger.info(f"Analyzing {media_type}: {file_path} for audience: {audience_params}")

        start_lock = time.time()
        with self.lock:
            lock_wait = time.time() - start_lock
            logger.info(f"Acquired GPU lock in {lock_wait:.2f}s")

            start_inference = time.time()
            results = self._run_analysis(file_path, media_type, audience_params)
            inference_time = time.time() - start_inference

            logger.info(f"Inference completed in {inference_time:.2f}s")
            if isinstance(results, dict):
                results["performance_metrics"] = {
                    "lock_wait_time": lock_wait,
                    "inference_time": inference_time
                }
            return results

    def _run_analysis(self, file_path, media_type, audience_params):
        # Cache Check (Skip hashing for URLs as they are transient/text-based)
        file_hash = None
        if media_type in ["video", "audio", "text"]:
            try:
                file_hash = calculate_file_hash(file_path)
                cache_path = os.path.join(CACHE_DIR, f"{file_hash}.pkl")
                if os.path.exists(cache_path):
                    logger.info(f"Cache hit for {file_path} (Hash: {file_hash})")
                    with open(cache_path, "rb") as f:
                        cached_data = pickle.load(f)
                        return self._process_predictions(cached_data["preds"], cached_data["segments"], audience_params)
            except Exception as e:
                logger.warning(f"Cache retrieval failed for {file_path}: {e}. Falling back to fresh inference.")

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
            temp_path = os.path.join(UPLOAD_DIR, f"{u_id}_url.txt")
            try:
                page = requests.get(file_path, timeout=10)
                soup = BeautifulSoup(page.content, 'html.parser')
                text = ' '.join([p.get_text() for p in soup.find_all('p')])

                # 10x Enhanced: Scrape Headline and CTAs specifically
                headlines = [h.get_text() for h in soup.find_all(['h1', 'h2'])]
                cta_buttons = [b.get_text() for b in soup.find_all(['button', 'a']) if len(b.get_text()) < 50]

                full_context = f"Headline: {' | '.join(headlines)}\nContent: {text}\nCTAs: {' | '.join(cta_buttons)}"

                with open(temp_path, "w") as f:
                    f.write(full_context)
                df_events = self.model.get_events_dataframe(text_path=temp_path)
            except Exception as e:
                if os.path.exists(temp_path): os.remove(temp_path)
                raise e
        else:
            raise ValueError(f"Unsupported media type: {media_type}")

        with torch.inference_mode():
            preds, segments = self.model.predict(events=df_events)

        # Save to Cache
        if file_hash:
            try:
                cache_path = os.path.join(CACHE_DIR, f"{file_hash}.pkl")
                # Atomic write to prevent corruption during concurrent access
                temp_cache = f"{cache_path}.tmp.{uuid.uuid4()}"
                with open(temp_cache, "wb") as f:
                    pickle.dump({"preds": preds, "segments": segments}, f)
                os.rename(temp_cache, cache_path)
                logger.info(f"Cached results for {file_path} (Hash: {file_hash})")
            except Exception as e:
                logger.error(f"Failed to cache results for {file_path}: {e}")

        # TRIBE v2 predicts on fsaverage5: (n_timesteps, 20484)
        # where the first 10242 vertices are Left Hem, and next 10242 are Right Hem.

        return self._process_predictions(preds, segments, audience_params)

    def _process_predictions(self, preds, segments, audience_params=None):
        if isinstance(preds, torch.Tensor):
            preds = preds.detach().cpu().numpy()

        results = {
            "timestamps": segments["onset"].tolist(),
            "neuro_metrics": {},
            "marketing_kpis": {}
        }

        # 1. Scientific ROI extraction (Neuro Metrics)
        for metric_name, indices in self.roi_map.items():
            lh_mask = np.isin(self.left_atlas, indices)
            rh_mask = np.isin(self.right_atlas, indices)
            full_mask = np.concatenate([lh_mask, rh_mask])

            if full_mask.shape[0] != preds.shape[1]:
                full_mask = full_mask[:preds.shape[1]]

            if np.any(full_mask):
                metric_series = preds[:, full_mask].mean(axis=1)
            else:
                metric_series = np.zeros(preds.shape[0])

            results["neuro_metrics"][metric_name] = self._normalize(metric_series).tolist()

        # 2. Map Neuro Metrics to Marketing KPIs
        # Mapping Logic:
        # Scroll-Stop Rate (Predicted) = Attention + VisualEngagement
        # Purchase Intent Score = Reward + Emotion - CognitiveLoad
        # Clarity Score = 100 - CognitiveLoad
        # Brand Recall Index = Memory + Attention

        neuro = results["neuro_metrics"]
        n_steps = len(results["timestamps"])

        results["marketing_kpis"]["ScrollStopRate"] = [
            min(100, (neuro["Attention"][i] * 0.7 + neuro["VisualEngagement"][i] * 0.3))
            for i in range(n_steps)
        ]
        results["marketing_kpis"]["PurchaseIntent"] = [
            max(0, min(100, (neuro["Reward"][i] * 0.6 + neuro["Emotion"][i] * 0.4 - neuro["CognitiveLoad"][i] * 0.2)))
            for i in range(n_steps)
        ]
        results["marketing_kpis"]["Clarity"] = [
            100 - neuro["CognitiveLoad"][i] for i in range(n_steps)
        ]
        results["marketing_kpis"]["BrandRecall"] = [
            min(100, (neuro["Memory"][i] * 0.8 + neuro["Attention"][i] * 0.2))
            for i in range(n_steps)
        ]

        # 10x Metrics
        results["marketing_kpis"]["ViralPotential"] = [
            min(100, (neuro["Emotion"][i] * 0.5 + neuro["VisualEngagement"][i] * 0.3 + (100 - neuro["CognitiveLoad"][i]) * 0.2))
            for i in range(n_steps)
        ]
        results["marketing_kpis"]["ConversionFriction"] = [
            max(0, min(100, (neuro["CognitiveLoad"][i] * 0.7 - neuro["Reward"][i] * 0.3)))
            for i in range(n_steps)
        ]

        # 3. Audience-Aware Weighting (Deterministic Calibration)
        if audience_params:
            results["marketing_kpis"] = self._apply_audience_weighting(
                results["marketing_kpis"],
                audience_params
            )

        # Winning Probability Calculation (Aggregated)
        pi = results["marketing_kpis"]["PurchaseIntent"]
        ssr = results["marketing_kpis"]["ScrollStopRate"]
        results["winning_probability"] = (sum(pi)/len(pi) * 0.7 + sum(ssr)/len(ssr) * 0.3)

        # 10x Spatial Attention Heatmap (Vertex-level peak)
        # We take the mean activation across the 'Attention' and 'VisualEngagement' ROIs
        attention_indices = self.roi_map["Attention"] + self.roi_map["VisualEngagement"]
        lh_mask = np.isin(self.left_atlas, attention_indices)
        rh_mask = np.isin(self.right_atlas, attention_indices)
        full_mask = np.concatenate([lh_mask, rh_mask])
        if full_mask.shape[0] != preds.shape[1]: full_mask = full_mask[:preds.shape[1]]

        # Get the vertex activations for these ROIs at the peak attention moment
        peak_time_idx = np.argmax(results["marketing_kpis"]["ScrollStopRate"])
        results["attention_heatmap"] = preds[peak_time_idx, full_mask].tolist()

        # 10x Predictive Creative Fatigue
        # Threshold: High attention and emotion density correlates with faster fatigue
        avg_attention = np.nanmean(results["marketing_kpis"]["ScrollStopRate"])
        avg_emotion = np.nanmean(neuro["Emotion"])

        # Handle potential NaNs from nanmean
        if np.isnan(avg_attention): avg_attention = 0.0
        if np.isnan(avg_emotion): avg_emotion = 0.0

        fatigue_score = (avg_attention * 0.4 + avg_emotion * 0.6)
        results["creative_fatigue"] = {
            "fatigue_index": min(100, fatigue_score), # 0-100 score
            "estimated_days": max(3, 30 - int(fatigue_score / 4))
        }

        # 10x Contextual 'Vibe' Extraction
        vibe_scores = {
            "Excitement": (neuro["Emotion"][peak_time_idx] * 0.6 + neuro["Reward"][peak_time_idx] * 0.4),
            "Trust": (neuro["Memory"][peak_time_idx] * 0.7 + (100 - neuro["CognitiveLoad"][peak_time_idx]) * 0.3),
            "Urgency": (neuro["Attention"][peak_time_idx] * 0.5 + neuro["CognitiveLoad"][peak_time_idx] * 0.5)
        }
        results["vibe_analysis"] = sorted(vibe_scores.items(), key=lambda x: x[1], reverse=True)[0][0]

        # MOI Analysis
        moi_events = []
        emotion_vals = neuro["Emotion"]
        for i in range(1, len(emotion_vals) - 1):
            if emotion_vals[i] > 80 and emotion_vals[i] > emotion_vals[i-1]:
                moi_events.append({
                    "timestamp": results["timestamps"][i],
                    "type": "Emotional Peak",
                    "value": emotion_vals[i]
                })
        results["moi_analysis"] = sorted(moi_events, key=lambda x: x['value'], reverse=True)[:5]

        return results

    def _apply_audience_weighting(self, kpis, params):
        """Deterministically adjust KPIs based on audience psychographics."""
        age = params.get("age", "25-34")
        platform = params.get("platform", "Meta")
        industry = params.get("industry", "D2C")
        awareness = params.get("awareness", "Cold")

        adjusted = {}
        for kpi_name, values in kpis.items():
            # Interaction effects for 10x Precision
            multipliers = []

            # Platform & Age interaction (The "TikTok/Gen Z" multiplier)
            if platform == "TikTok" and age == "18-24":
                if kpi_name == "ScrollStopRate": multipliers.append(0.75) # Brutal competition
                if kpi_name == "ViralPotential": multipliers.append(1.3) # Higher upside

            # B2B/LinkedIn Friction sensitivity
            if platform == "LinkedIn" or industry == "SaaS":
                if kpi_name == "Clarity": multipliers.append(1.2) # Clarity is king in B2B
                if kpi_name == "ConversionFriction": multipliers.append(1.1)

            # Awareness Level calibration
            if awareness == "Cold":
                if kpi_name == "PurchaseIntent": multipliers.append(0.7)
                if kpi_name == "ScrollStopRate": multipliers.append(1.1) # Hook is everything
            elif awareness == "Hot":
                if kpi_name == "PurchaseIntent": multipliers.append(1.4)
                if kpi_name == "BrandRecall": multipliers.append(1.2)

            # 10x Industry Psychographics
            if industry == "Info Products":
                if kpi_name == "PurchaseIntent": multipliers.append(1.15)
                if kpi_name == "Emotion": multipliers.append(1.1) # Hype matters

            if industry == "Professional Services":
                if kpi_name == "BrandRecall": multipliers.append(1.3)
                if kpi_name == "Clarity": multipliers.append(1.2)

            # Compute final multiplier
            final_m = np.prod(multipliers) if multipliers else 1.0
            adjusted[kpi_name] = [min(100, v * final_m) for v in values]

        return adjusted

    def _normalize(self, series):
        s_min, s_max = series.min(), series.max()
        if s_max - s_min == 0:
            return series * 0
        return ((series - s_min) / (s_max - s_min)) * 100
