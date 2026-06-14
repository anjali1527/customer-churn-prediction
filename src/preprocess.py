import pandas as pd
from sklearn.preprocessing import LabelEncoder


# Columns that are never useful as features
_DROP_PATTERNS = ["customerid", "id", "rownum", "unnamed", "index", "uuid"]

# Known binary yes/no columns that should map to 1/0
_BINARY_MAP = {"yes": 1, "no": 0, "true": 1, "false": 0, "y": 1, "n": 0}


def preprocess_data(df: pd.DataFrame, target_col: str = "Churn") -> pd.DataFrame:

    df = df.copy()

    # ── 1. Drop ID / index columns ────────────────────────────────────────────
    drop_cols = [
        c for c in df.columns
        if any(p in c.lower() for p in _DROP_PATTERNS)
    ]
    df.drop(columns=drop_cols, inplace=True, errors="ignore")

    # ── 2. Numeric coercion for known problem columns ─────────────────────────
    for col in ["TotalCharges", "MonthlyCharges", "tenure"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── 3. Encode target if present ───────────────────────────────────────────
    if target_col in df.columns:
        t = df[target_col]
        if t.dtype == object:
            df[target_col] = t.str.strip().str.lower().map(_BINARY_MAP).fillna(0).astype(int)
        else:
            df[target_col] = pd.to_numeric(t, errors="coerce").fillna(0).astype(int)

    # ── 4. Handle object columns ──────────────────────────────────────────────
    le = LabelEncoder()
    for col in df.select_dtypes(include=["object"]).columns:
        if col == target_col:
            continue
        # Try binary map first
        lower_vals = df[col].str.strip().str.lower()
        if lower_vals.isin(list(_BINARY_MAP.keys()) + [""]).all():
            df[col] = lower_vals.map(_BINARY_MAP).fillna(0).astype(int)
        else:
            df[col] = le.fit_transform(df[col].astype(str))

    # ── 5. Fill remaining NaN ─────────────────────────────────────────────────
    df.fillna(0, inplace=True)

    # ── 6. Ensure all columns are numeric ────────────────────────────────────
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df
