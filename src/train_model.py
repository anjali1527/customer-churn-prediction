import argparse
import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

from preprocess import preprocess_data


def train_model(
    data_path: str,
    model_path: str = "../models/churn_model.pkl",
    target_col: str = "Churn",
) -> object:
    """
    Full training pipeline.

    Parameters
    ----------
    data_path  : Path to raw CSV training file
    model_path : Where to save the trained model
    target_col : Name of the binary churn target column

    Returns
    -------
    Trained RandomForestClassifier
    """
    print("=" * 60)
    print("  NEXUS · Model Training Pipeline")
    print("=" * 60)

    # ── Load ──────────────────────────────────────────────────────────────────
    print(f"\n[1/5]  Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"       Rows: {len(df):,}   Columns: {df.shape[1]}")

    # ── Preprocess ────────────────────────────────────────────────────────────
    print("\n[2/5]  Preprocessing...")
    df = preprocess_data(df, target_col=target_col)

    if target_col not in df.columns:
        raise ValueError(
            f"Target column '{target_col}' not found after preprocessing. "
            f"Available columns: {list(df.columns)}"
        )

    X = df.drop(columns=[target_col])
    y = df[target_col]

    print(f"       Features: {X.shape[1]}")
    print(f"       Class balance — Churn: {y.mean():.1%}  No-Churn: {1-y.mean():.1%}")

    # ── Split ─────────────────────────────────────────────────────────────────
    print("\n[3/5]  Splitting (80/20 stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"       Train: {len(X_train):,}   Test: {len(X_test):,}")

    # ── Train ─────────────────────────────────────────────────────────────────
    print("\n[4/5]  Training Random Forest (200 trees)...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # ── Evaluate ──────────────────────────────────────────────────────────────
    print("\n[5/5]  Evaluating...")
    preds     = model.predict(X_test)
    probs     = model.predict_proba(X_test)[:, 1]
    acc       = accuracy_score(y_test, preds)
    auc       = roc_auc_score(y_test, probs)

    # 5-fold CV AUC
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_auc = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")

    print("\n  ┌─ Metrics ─────────────────────────────────────")
    print(f"  │  Accuracy  : {acc:.4f}")
    print(f"  │  ROC-AUC   : {auc:.4f}")
    print(f"  │  CV AUC    : {cv_auc.mean():.4f} ± {cv_auc.std():.4f}")
    print("  └───────────────────────────────────────────────")

    print("\n  Classification Report:")
    print(classification_report(y_test, preds, target_names=["No Churn", "Churn"]))

    # ── Save ──────────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"\n  Model saved → {model_path}")

    # Save feature list alongside model
    feat_path = model_path.replace(".pkl", "_features.txt")
    with open(feat_path, "w") as f:
        f.write("\n".join(list(X.columns)))
    print(f"  Features   → {feat_path}")
    print("\n" + "=" * 60)

    return model


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEXUS Churn Model Trainer")
    parser.add_argument("--data",  required=True, help="Path to training CSV")
    parser.add_argument("--model", default="../models/churn_model.pkl", help="Output model path")
    parser.add_argument("--target", default="Churn", help="Target column name")
    args = parser.parse_args()

    train_model(args.data, args.model, args.target)
