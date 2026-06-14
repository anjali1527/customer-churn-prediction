import os
import joblib
import pandas as pd
import numpy as np

from preprocess import preprocess_data


MODEL_PATH    = os.path.join(os.path.dirname(__file__), "../models/churn_model.pkl")
FALLBACK_PATH = os.path.join(os.path.dirname(__file__), "churn_model.pkl")


class ChurnPredictor:

    def __init__(self, model_path: str = None):
        # ── Locate model file ─────────────────────────────────────────────────
        path = model_path or MODEL_PATH
        if not os.path.exists(path):
            path = FALLBACK_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"No trained model found at '{path}'.\n"
                "Run:  python pipeline.py --data <your_csv>  to train first."
            )

        self.model = joblib.load(path)

        # ── Extract feature names ─────────────────────────────────────────────
        if hasattr(self.model, "feature_names_in_"):
            self.features = list(self.model.feature_names_in_)
        else:
            # Try loading companion features file
            feat_file = path.replace(".pkl", "_features.txt")
            if os.path.exists(feat_file):
                with open(feat_file) as f:
                    self.features = [ln.strip() for ln in f if ln.strip()]
            else:
                self.features = []

    # ── Feature preparation ────────────────────────────────────────────────────
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess any raw DataFrame and align columns to training features.
        Unknown columns are dropped; missing features are filled with 0.
        """
        df = preprocess_data(df)

        # Remove target if accidentally included
        for col in ["Churn", "churn", "CHURN"]:
            if col in df.columns:
                df = df.drop(columns=[col])

        # Align to training feature set
        if self.features:
            df = df.reindex(columns=self.features, fill_value=0)

        return df

    # ── Batch prediction ───────────────────────────────────────────────────────
    def predict_batch(self, df: pd.DataFrame):
        """
        Predict for a full DataFrame.

        Returns
        -------
        preds : np.ndarray of int (0/1)
        probs : np.ndarray of float (churn probability)
        """
        try:
            df_model = self.prepare_features(df)
            preds    = self.model.predict(df_model)
            probs    = self.model.predict_proba(df_model)[:, 1]
            return preds, probs
        except Exception as e:
            raise RuntimeError(f"Batch prediction failed: {e}") from e

    # ── Single prediction ──────────────────────────────────────────────────────
    def predict(self, input_dict: dict) -> dict:
        """
        Predict for one customer (dict of feature → value).

        Returns
        -------
        dict with keys: prediction (int), probability (float)
        or dict with key: error (str)
        """
        try:
            df       = pd.DataFrame([input_dict])
            df_model = self.prepare_features(df)
            pred     = int(self.model.predict(df_model)[0])
            prob     = float(self.model.predict_proba(df_model)[0][1])
            return {"prediction": pred, "probability": prob}
        except Exception as e:
            return {"error": str(e)}
