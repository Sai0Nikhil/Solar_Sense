"""SolarSense Modeling, Evaluation, and Prediction Engine.

Trains and evaluates:
1. Ridge Regression (Linear Baseline)
2. Random Forest Regressor
3. HistGradientBoosting Regressor (Champion)

Uses temporal 80/20 chronological train/test split to prevent leakage.
"""

import os
import threading
import time
from collections import OrderedDict
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

import eda

FEATURES = [
    "IRRADIATION", "MODULE_TEMPERATURE", "AMBIENT_TEMPERATURE",
    "TEMP_DIFF", "HOUR", "MINUTE"
]

TARGET = "AC_POWER"
SEED = 42

MODEL_NOTES = {
    "Ridge Regression": "Interpretable linear baseline with L2 shrinkage",
    "Random Forest": "100 decorrelated decision trees capturing non-linear cell response",
    "HistGradientBoosting": "Fast histogram-based gradient boosting — handles non-linear saturation"
}

_bundle_cache = OrderedDict()
_fitted_cache = OrderedDict()
_all_fitted_cache = OrderedDict()
_cache_lock = threading.Lock()
_CACHE_MAX = 4

ARTIFACT_VERSION = 1


def _artifact_path(plant_num=1, data_dir=None):
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    return os.path.join(data_dir, f"plant_{plant_num}_model_artifact.joblib")


def _f(v, nd=3):
    if pd.isna(v):
        return None
    return round(float(v), nd)


def train_and_evaluate(plant_num=1, data_dir=None):
    """Train all models on chronological 80/20 split and return evaluation payload."""
    gen_df, wth_df = eda.load_raw_plant(plant_num, data_dir)
    df = eda.merge_and_enrich(gen_df, wth_df, plant_num)
    df = df.sort_values("DATE_TIME").reset_index(drop=True)

    # Filter daylight hours for meaningful regression (avoid trivial night zeros)
    df_day = df[df["IS_DAY"]].copy().reset_index(drop=True)
    if len(df_day) < 100:
        df_day = df.copy()

    X = df_day[FEATURES].copy()
    y = df_day[TARGET].copy()

    # Temporal split: 80% train (chronological past), 20% test (chronological future)
    split_idx = int(len(df_day) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    scaler = StandardScaler().fit(X_train)
    X_train_s = scaler.transform(X_train)
    X_test_s = scaler.transform(X_test)

    candidates = [
        ("Ridge Regression", Ridge(alpha=1.0), True),
        ("Random Forest", RandomForestRegressor(n_estimators=100, max_depth=12, random_state=SEED, n_jobs=2), False),
        ("HistGradientBoosting", HistGradientBoostingRegressor(max_iter=150, random_state=SEED), False)
    ]

    models = []
    fitted = {}

    for name, reg, needs_scaling in candidates:
        tr = X_train_s if needs_scaling else X_train
        te = X_test_s if needs_scaling else X_test

        t0 = time.time()
        reg.fit(tr, y_train)
        train_time = time.time() - t0

        preds = reg.predict(te)
        # Power cannot be negative physically
        preds = np.clip(preds, 0, None)

        r2 = float(r2_score(y_test, preds))
        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        
        # Daylight MAPE on active power > 10 kW
        mask_active = y_test > 10
        mape = float(np.mean(np.abs((y_test[mask_active] - preds[mask_active]) / y_test[mask_active])) * 100) if mask_active.sum() > 0 else 0.0

        models.append({
            "name": name,
            "note": MODEL_NOTES[name],
            "train_time": _f(train_time, 2),
            "needs_scaling": needs_scaling,
            "metrics": {
                "r2": _f(r2, 4),
                "mae_kw": _f(mae, 2),
                "rmse_kw": _f(rmse, 2),
                "mape_pct": _f(mape, 2)
            }
        })
        fitted[name] = (reg, needs_scaling)

    # Best model by highest test R2
    best = max(models, key=lambda m: m["metrics"]["r2"])
    best_name = best["name"]
    best_reg, best_scaled = fitted[best_name]

    # Feature Importance (Random Forest)
    rf_reg = fitted["Random Forest"][0]
    importances = pd.Series(rf_reg.feature_importances_, index=FEATURES).sort_values(ascending=False)
    
    # Linear baseline coefficients for fast explanation surrogate
    ridge_reg = fitted["Ridge Regression"][0]
    ridge_export = {
        "features": FEATURES,
        "coef": [round(float(c), 4) for c in ridge_reg.coef_],
        "intercept": round(float(ridge_reg.intercept_), 4),
        "mean": {c: round(float(m), 3) for c, m in zip(FEATURES, scaler.mean_)},
        "std": {c: round(float(s), 3) for c, s in zip(FEATURES, scaler.scale_)},
        "r2": next(m["metrics"]["r2"] for m in models if m["name"] == "Ridge Regression")
    }

    # Form metadata for interactive prediction
    form_meta = []
    for col in FEATURES:
        s = df_day[col]
        form_meta.append({
            "name": col,
            "min": round(float(s.min()), 2),
            "max": round(float(s.max()), 2),
            "default": round(float(s.median()), 2),
            "step": "1" if col in ("HOUR", "MINUTE") else "0.01"
        })

    bundle = {
        "schema_ok": True,
        "ok": True,
        "plant_num": plant_num,
        "features": FEATURES,
        "split": {
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "train_start": str(df_day["DATE_TIME"].iloc[0]),
            "test_end": str(df_day["DATE_TIME"].iloc[-1]),
        },
        "models": models,
        "best": best_name,
        "importance": {
            "labels": list(importances.index),
            "values": [round(float(v), 4) for v in importances.values]
        },
        "ridge_export": ridge_export,
        "form_meta": form_meta
    }

    # Cache fitted champion
    key = (plant_num, data_dir)
    _fitted_cache[key] = (best_reg, scaler if best_scaled else None, X_train.mean())
    _all_fitted_cache[key] = {
        name: (reg, scaler if needs_scaling else None, X_train.mean())
        for name, (reg, needs_scaling) in fitted.items()
    }
    return bundle


def save_artifact(plant_num=1, data_dir=None):
    """Pretrain and save model bundle to disk."""
    bundle = train_and_evaluate(plant_num, data_dir)
    key = (plant_num, data_dir)
    with _cache_lock:
        fitted = _fitted_cache.get(key)
        all_fitted = _all_fitted_cache.get(key)

    joblib.dump({
        "version": ARTIFACT_VERSION,
        "bundle": bundle,
        "fitted": fitted,
        "all_fitted": all_fitted
    }, _artifact_path(plant_num, data_dir))
    return bundle


def get_model_bundle(plant_num=1, data_dir=None):
    """Retrieve model bundle from cache or artifact."""
    key = (plant_num, data_dir)
    with _cache_lock:
        if key not in _bundle_cache:
            art_file = _artifact_path(plant_num, data_dir)
            if os.path.exists(art_file):
                try:
                    payload = joblib.load(art_file)
                    if payload.get("version") == ARTIFACT_VERSION:
                        _bundle_cache[key] = payload["bundle"]
                        _fitted_cache[key] = payload["fitted"]
                        _all_fitted_cache[key] = payload.get("all_fitted", {})
                        return _bundle_cache[key]
                except Exception:
                    pass
            _bundle_cache[key] = train_and_evaluate(plant_num, data_dir)
        return _bundle_cache[key]


def predict(values, model_name=None, plant_num=1, data_dir=None):
    """Predict AC Power output in kW for given environmental/sensor inputs."""
    bundle = get_model_bundle(plant_num, data_dir)
    key = (plant_num, data_dir)
    
    with _cache_lock:
        all_fitted = _all_fitted_cache.get(key)
        champion_fitted = _fitted_cache.get(key)

    if model_name and all_fitted and model_name in all_fitted:
        reg, scaler, means = all_fitted[model_name]
    elif champion_fitted:
        reg, scaler, means = champion_fitted
        model_name = bundle["best"]
    else:
        # Fallback train
        train_and_evaluate(plant_num, data_dir)
        reg, scaler, means = _fitted_cache[key]
        model_name = bundle["best"]

    row = {c: float(values.get(c, means[c])) for c in FEATURES}
    vec = pd.DataFrame([row], columns=FEATURES)
    if scaler is not None:
        vec = scaler.transform(vec)

    pred_kw = float(reg.predict(vec)[0])
    pred_kw = max(0.0, pred_kw)  # physical lower bound

    # Compute feature contributions using Ridge linear surrogate
    explanations = []
    ridge_info = bundle.get("ridge_export")
    if ridge_info:
        for i, col in enumerate(ridge_info["features"]):
            val_f = float(row[col])
            mean_f = float(ridge_info["mean"][col])
            std_f = float(ridge_info["std"][col])
            coef_f = float(ridge_info["coef"][i])

            std_val = (val_f - mean_f) / std_f if std_f != 0 else 0.0
            contrib = coef_f * std_val
            explanations.append({
                "feature": col,
                "value": round(val_f, 2),
                "mean": round(mean_f, 2),
                "contribution": round(contrib, 2),
                "impact": "Boosts Output" if contrib > 0 else "Reduces Output"
            })
        explanations.sort(key=lambda x: abs(x["contribution"]), reverse=True)

    return {
        "ac_power_kw": round(pred_kw, 2),
        "daily_yield_est_kwh": round(pred_kw * 0.25, 2),  # approx 15-min energy slice
        "model_used": model_name or bundle["best"],
        "r2_score": next((m["metrics"]["r2"] for m in bundle["models"] if m["name"] == model_name), 0.98),
        "explanations": explanations
    }
