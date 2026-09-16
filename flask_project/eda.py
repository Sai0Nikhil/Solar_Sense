"""SolarSense EDA, Data Loading, and Imputation Analytics Engine.

Handles multi-plant generation and weather sensor synchronization,
diurnal cycle decomposition, inverter efficiency tracking,
and comparative time-series imputation.

Imputation policy (3-tier):
  - Gaps ≤ 4 slots (≤ 1 h)  → Time Linear Spline Interpolation
  - Gaps > 4 slots (> 1 h, daytime) → Diurnal Profile Matching
  - Night gaps (any length)  → Zero-clamped (IRRADIATION physically = 0)
"""

import os
import threading
from collections import OrderedDict
import numpy as np
import pandas as pd

PLANT_1_ID = 4135001
PLANT_2_ID = 4136001

NUMERIC_COLS = [
    "DC_POWER", "AC_POWER", "DAILY_YIELD", "TOTAL_YIELD",
    "AMBIENT_TEMPERATURE", "MODULE_TEMPERATURE", "IRRADIATION",
    "EFFICIENCY", "TEMP_DIFF"
]

DISTRIBUTION_COLS = [
    "AC_POWER", "DC_POWER", "IRRADIATION",
    "MODULE_TEMPERATURE", "AMBIENT_TEMPERATURE", "TEMP_DIFF", "DAILY_YIELD", "EFFICIENCY"
]

STANDARDIZE_COLS = [
    "IRRADIATION", "MODULE_TEMPERATURE", "AMBIENT_TEMPERATURE", "TEMP_DIFF"
]

TARGET_COL = "AC_POWER"

WEATHER_IMPUTE_COLS = ["AMBIENT_TEMPERATURE", "MODULE_TEMPERATURE", "IRRADIATION"]

COLUMN_META = {
    "DATE_TIME": ("Temporal", "timestamp", "15-minute interval timestamp"),
    "PLANT_ID": ("Identity", "identifier", "Solar farm unique ID (4135001 or 4136001)"),
    "SOURCE_KEY": ("Identity", "inverter_id", "String inverter unique serial hash (22 inverters)"),
    "WEATHER_SENSOR_KEY": ("Identity", "sensor_id", "Central weather station sensor ID"),
    "DC_POWER": ("Generation", "input_power", "Direct current generation from photovoltaic arrays (kW)"),
    "AC_POWER": ("Generation", "output_power", "Alternating current power delivered by inverter (kW)"),
    "DAILY_YIELD": ("Yield", "energy", "Cumulative energy generated since dawn (kWh)"),
    "TOTAL_YIELD": ("Yield", "lifetime_energy", "Lifetime inverter energy output counter (kWh)"),
    "AMBIENT_TEMPERATURE": ("Weather", "meteorological", "Air temperature at central weather monitoring station (°C)"),
    "MODULE_TEMPERATURE": ("Weather", "surface_temp", "Solar panel thermocouple surface temperature (°C)"),
    "IRRADIATION": ("Weather", "solar_flux", "Global Horizontal Irradiance (GHI) measurement (kW/m²)"),
    "EFFICIENCY": ("Derived", "inverter_health", "Inverter conversion efficiency percentage (AC / DC * 100)"),
    "TEMP_DIFF": ("Derived", "thermal_stress", "Module heating delta (Module Temp - Ambient Temp) (°C)"),
    "HOUR": ("Temporal", "diurnal", "Hour of day (0-23) capturing diurnal solar elevation"),
    "MINUTE": ("Temporal", "sub_interval", "Minute within hour (0, 15, 30, 45)"),
}

_bundle_cache = OrderedDict()
_cache_lock = threading.RLock()
_CACHE_MAX = 4


def _f(value, nd=2):
    if pd.isna(value):
        return None
    return round(float(value), nd)


def _i(value):
    if pd.isna(value):
        return 0
    return int(value)


def _histogram(series, bins=12):
    clean = series.dropna()
    if len(clean) == 0:
        return {"labels": [], "counts": [], "mean": None, "std": None}
    counts, edges = np.histogram(clean, bins=bins)
    labels = [f"{edges[i]:.1f}–{edges[i+1]:.1f}" for i in range(len(counts))]
    return {
        "labels": labels,
        "counts": [_i(c) for c in counts],
        "mean": _f(clean.mean(), 2),
        "std": _f(clean.std(), 2)
    }


def _heat_color(val):
    if val is None or np.isnan(val):
        return "transparent"
    # amber heat scale
    v = max(-1.0, min(1.0, float(val)))
    if v >= 0:
        alpha = v ** 0.8
        return f"rgba(217, 166, 63, {alpha * 0.85:.2f})"
    else:
        alpha = abs(v) ** 0.8
        return f"rgba(198, 93, 85, {alpha * 0.75:.2f})"


def load_raw_plant(plant_num=1, data_dir=None):
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    gen_file = os.path.join(data_dir, f"Plant_{plant_num}_Generation_Data.csv")
    wth_file = os.path.join(data_dir, f"Plant_{plant_num}_Weather_Sensor_Data.csv")

    if not os.path.exists(gen_file) or not os.path.exists(wth_file):
        raise FileNotFoundError(f"Dataset files for Plant {plant_num} not found in {data_dir}")

    gen_df = pd.read_csv(gen_file)
    if plant_num == 1:
        gen_df["DATE_TIME"] = pd.to_datetime(gen_df["DATE_TIME"], format="%d-%m-%Y %H:%M", errors="coerce")
    else:
        gen_df["DATE_TIME"] = pd.to_datetime(gen_df["DATE_TIME"], errors="coerce")

    wth_df = pd.read_csv(wth_file)
    wth_df["DATE_TIME"] = pd.to_datetime(wth_df["DATE_TIME"], errors="coerce")

    return gen_df, wth_df


# ---------------------------------------------------------------------------
# 3-Tier Imputation Engine
# ---------------------------------------------------------------------------

def impute_weather_gaps(wth_df):
    """Apply 3-tier imputation to the weather sensor dataframe.

    Returns
    -------
    imputed_df : pd.DataFrame
        Complete continuous weather dataframe at 15-min cadence.
    gap_audit : list[dict]
        One entry per contiguous gap event with: start, end, n_slots,
        duration_min, time_of_day, strategy_applied.
    raw_count : int
        Number of originally observed timestamps (before reindexing).
    """
    df = wth_df.sort_values("DATE_TIME").copy()
    raw_count = len(df)

    full_range = pd.date_range(
        start=df["DATE_TIME"].min(),
        end=df["DATE_TIME"].max(),
        freq="15min"
    )

    # Reindex to full continuous range (missing rows become NaN)
    df = df.set_index("DATE_TIME").reindex(full_range)
    df.index.name = "DATE_TIME"

    # Forward-fill PLANT_ID / sensor key columns (identity, not numeric)
    for col in ["PLANT_ID"]:
        if col in df.columns:
            df[col] = df[col].ffill().bfill()

    # Build hourly diurnal means from the *observed* (non-NaN) data
    df["_HOUR"] = df.index.hour
    diurnal_means = {}
    for col in WEATHER_IMPUTE_COLS:
        diurnal_means[col] = (
            df[col].groupby(df["_HOUR"]).mean()
        )

    # Identify contiguous gap runs (consecutive NaN rows in IRRADIATION)
    gap_audit = []
    is_missing = df["IRRADIATION"].isna()
    in_gap = False
    gap_start = None

    for ts, missing in is_missing.items():
        if missing and not in_gap:
            in_gap = True
            gap_start = ts
        elif not missing and in_gap:
            in_gap = False
            gap_end = ts - pd.Timedelta(minutes=15)
            gap_slots = int((gap_end - gap_start).total_seconds() / 900) + 1
            hour = gap_start.hour
            is_night = not (6 <= hour <= 18)
            strategy = (
                "Zero-Clamp (Night)" if is_night
                else ("Linear Spline" if gap_slots <= 4 else "Diurnal Profile Matching")
            )
            gap_audit.append({
                "start": gap_start.strftime("%Y-%m-%d %H:%M"),
                "end": gap_end.strftime("%Y-%m-%d %H:%M"),
                "n_slots": gap_slots,
                "duration_min": gap_slots * 15,
                "hour": hour,
                "is_night": is_night,
                "strategy": strategy,
            })

    # Close open gap at end
    if in_gap:
        gap_end = df.index[-1]
        gap_slots = int((gap_end - gap_start).total_seconds() / 900) + 1
        hour = gap_start.hour
        is_night = not (6 <= hour <= 18)
        strategy = (
            "Zero-Clamp (Night)" if is_night
            else ("Linear Spline" if gap_slots <= 4 else "Diurnal Profile Matching")
        )
        gap_audit.append({
            "start": gap_start.strftime("%Y-%m-%d %H:%M"),
            "end": gap_end.strftime("%Y-%m-%d %H:%M"),
            "n_slots": gap_slots,
            "duration_min": gap_slots * 15,
            "hour": hour,
            "is_night": is_night,
            "strategy": strategy,
        })

    # ---- Apply imputation column by column ----
    for col in WEATHER_IMPUTE_COLS:
        series = df[col].copy()
        dmeans = diurnal_means[col]

        # Pass 1: linear spline for short gaps (≤ 4 consecutive NaN slots)
        # We interpolate everything linearly first as a baseline
        series_linear = series.interpolate(method="time").bfill().ffill()

        # Pass 2: for long daytime gaps, override with diurnal pattern
        # Build a mask of which NaN positions came from long-gap events
        long_gap_mask = pd.Series(False, index=df.index)
        for gap in gap_audit:
            if not gap["is_night"] and gap["n_slots"] > 4:
                long_gap_mask[gap["start"]:gap["end"]] = True

        # For long daytime gaps: use diurnal mean for that hour
        diurnal_fill = df["_HOUR"].map(dmeans)

        # For night gaps: zero-clamp irradiation, use diurnal for temps
        night_gap_mask = pd.Series(False, index=df.index)
        for gap in gap_audit:
            if gap["is_night"]:
                night_gap_mask[gap["start"]:gap["end"]] = True

        # Compose final series
        final = series_linear.copy()
        # Override long daytime gaps with diurnal
        final[long_gap_mask & series.isna()] = diurnal_fill[long_gap_mask & series.isna()]
        # Override night gaps
        if col == "IRRADIATION":
            final[night_gap_mask & series.isna()] = 0.0
        else:
            final[night_gap_mask & series.isna()] = diurnal_fill[night_gap_mask & series.isna()]

        df[col] = final

    df = df.drop(columns=["_HOUR"]).reset_index()
    return df, gap_audit, raw_count


def evaluate_imputation_strategies(wth_df):
    df_sorted = wth_df.sort_values("DATE_TIME").copy()

    full_range = pd.date_range(start=df_sorted["DATE_TIME"].min(), end=df_sorted["DATE_TIME"].max(), freq="15min")
    missing_timestamps = full_range.difference(df_sorted["DATE_TIME"])
    missing_count = len(missing_timestamps)

    df_day = df_sorted[df_sorted["IRRADIATION"] > 0.05].copy()
    if len(df_day) < 100:
        df_day = df_sorted.copy()

    np.random.seed(42)
    mask = np.random.rand(len(df_day)) < 0.10

    targets = ["AMBIENT_TEMPERATURE", "MODULE_TEMPERATURE", "IRRADIATION"]
    results = {}

    for col in targets:
        true_vals = df_day[col].values
        corrupted = true_vals.copy()
        corrupted[mask] = np.nan

        series = pd.Series(corrupted, index=df_day["DATE_TIME"])

        # 1. Forward Fill
        s_ffill = series.ffill().bfill().values
        mae_ffill = float(np.nanmean(np.abs(true_vals[mask] - s_ffill[mask])))
        rmse_ffill = float(np.sqrt(np.nanmean((true_vals[mask] - s_ffill[mask]) ** 2)))

        # 2. Time Linear Interpolation
        s_linear = series.interpolate(method="time").ffill().bfill().values
        mae_linear = float(np.nanmean(np.abs(true_vals[mask] - s_linear[mask])))
        rmse_linear = float(np.sqrt(np.nanmean((true_vals[mask] - s_linear[mask]) ** 2)))

        # 3. Diurnal Pattern
        df_day["corrupted_" + col] = corrupted
        hourly_means = df_day.groupby(df_day["DATE_TIME"].dt.hour)["corrupted_" + col].transform("mean")
        s_diurnal = np.where(np.isnan(corrupted), hourly_means, corrupted)
        mae_diurnal = float(np.nanmean(np.abs(true_vals[mask] - s_diurnal[mask])))
        rmse_diurnal = float(np.sqrt(np.nanmean((true_vals[mask] - s_diurnal[mask]) ** 2)))

        results[col] = {
            "mean": _f(np.mean(true_vals), 2),
            "std": _f(np.std(true_vals), 2),
            "forward_fill": {"mae": _f(mae_ffill, 3), "rmse": _f(rmse_ffill, 3)},
            "linear_interp": {"mae": _f(mae_linear, 3), "rmse": _f(rmse_linear, 3)},
            "diurnal_pattern": {"mae": _f(mae_diurnal, 3), "rmse": _f(rmse_diurnal, 3)},
            "best_strategy": "Time Linear Interpolation" if rmse_linear <= rmse_ffill and rmse_linear <= rmse_diurnal else "Diurnal Pattern"
        }

    return {
        "missing_timestamps_count": missing_count,
        "total_expected_intervals": len(full_range),
        "actual_sensor_intervals": len(df_sorted),
        "coverage_pct": _f((len(df_sorted) / len(full_range)) * 100, 2),
        "metrics_by_sensor": results,
        "chart_labels": ["Irradiation", "Module Temp", "Ambient Temp"],
        "chart_ffill_rmse": [results["IRRADIATION"]["forward_fill"]["rmse"], results["MODULE_TEMPERATURE"]["forward_fill"]["rmse"], results["AMBIENT_TEMPERATURE"]["forward_fill"]["rmse"]],
        "chart_linear_rmse": [results["IRRADIATION"]["linear_interp"]["rmse"], results["MODULE_TEMPERATURE"]["linear_interp"]["rmse"], results["AMBIENT_TEMPERATURE"]["linear_interp"]["rmse"]],
        "chart_diurnal_rmse": [results["IRRADIATION"]["diurnal_pattern"]["rmse"], results["MODULE_TEMPERATURE"]["diurnal_pattern"]["rmse"], results["AMBIENT_TEMPERATURE"]["diurnal_pattern"]["rmse"]],
        "affected": [
            {
                "name": "Weather Sensor Stream (15-min Intervals)",
                "count": missing_count,
                "pct": _f((missing_count / len(full_range)) * 100, 2),
                "non_null_pct": _f((len(df_sorted) / len(full_range)) * 100, 2),
                "impute_method": "Time Linear Spline"
            }
        ]
    }


def merge_and_enrich(gen_df, wth_df, plant_num=1):
    merged = pd.merge(
        gen_df, wth_df,
        on=["DATE_TIME", "PLANT_ID"],
        suffixes=("_GEN", "_WEATHER"),
        how="inner"
    )

    if "SOURCE_KEY_GEN" in merged.columns:
        merged["SOURCE_KEY"] = merged["SOURCE_KEY_GEN"]
    if "SOURCE_KEY_WEATHER" in merged.columns:
        merged["WEATHER_SENSOR_KEY"] = merged["SOURCE_KEY_WEATHER"]

    if plant_num == 1:
        merged["EFFICIENCY"] = np.where(
            merged["DC_POWER"] > 10,
            (merged["AC_POWER"] / (merged["DC_POWER"] / 10.0)) * 100.0,
            np.nan
        )
    else:
        merged["EFFICIENCY"] = np.where(
            merged["DC_POWER"] > 0,
            (merged["AC_POWER"] / merged["DC_POWER"]) * 100.0,
            np.nan
        )

    merged["EFFICIENCY"] = merged["EFFICIENCY"].clip(0, 100)
    merged["TEMP_DIFF"] = merged["MODULE_TEMPERATURE"] - merged["AMBIENT_TEMPERATURE"]
    merged["HOUR"] = merged["DATE_TIME"].dt.hour
    merged["MINUTE"] = merged["DATE_TIME"].dt.minute
    merged["DATE"] = merged["DATE_TIME"].dt.date
    merged["IS_DAY"] = (merged["IRRADIATION"] > 0) | (merged["HOUR"].between(6, 18))

    return merged


def build_plant_bundle(plant_num=1, data_dir=None):
    gen_df, wth_df = load_raw_plant(plant_num, data_dir)

    # ---- Apply 3-tier imputation to weather data ----
    wth_imputed, gap_audit, raw_wth_count = impute_weather_gaps(wth_df)

    df = merge_and_enrich(gen_df, wth_imputed, plant_num)

    inverters = df["SOURCE_KEY"].unique()
    n_inverters = len(inverters)

    overview = {
        "plant_num": plant_num,
        "plant_id": PLANT_1_ID if plant_num == 1 else PLANT_2_ID,
        "rows": _i(len(df)),
        "columns": _i(df.shape[1]),
        "total_records": len(df),
        "n_inverters": n_inverters,
        "start_date": df["DATE_TIME"].min().strftime("%Y-%m-%d"),
        "end_date": df["DATE_TIME"].max().strftime("%Y-%m-%d"),
        "days_span": _i((df["DATE_TIME"].max() - df["DATE_TIME"].min()).days + 1),
        "peak_dc_kw": _f(df["DC_POWER"].max()),
        "peak_ac_kw": _f(df["AC_POWER"].max()),
        "avg_day_ac_kw": _f(df[df["IS_DAY"]]["AC_POWER"].mean()),
        "avg_daily_yield_kwh": _f(df.groupby(["DATE", "SOURCE_KEY"])["DAILY_YIELD"].max().mean()),
        "max_ambient_temp": _f(df["AMBIENT_TEMPERATURE"].max()),
        "max_module_temp": _f(df["MODULE_TEMPERATURE"].max()),
        "max_irradiation": _f(df["IRRADIATION"].max(), 3),
        "avg_efficiency": _f(df["EFFICIENCY"].dropna().mean()),
        "completeness": _f((raw_wth_count / max(len(wth_imputed), 1)) * 100, 1),
    }

    # Features Registry
    registry = []
    for col in df.columns:
        if col in ("DATE", "IS_DAY", "SOURCE_KEY_GEN", "SOURCE_KEY_WEATHER"):
            continue
        group, role, note = COLUMN_META.get(col, ("Derived", "feature", "Calculated solar engineering field"))
        series = df[col]
        registry.append({
            "name": col,
            "group": group,
            "role": role,
            "note": note,
            "dtype": str(series.dtype),
            "non_null": _i(series.notna().sum()),
            "missing": _i(series.isna().sum()),
            "non_null_pct": _f(series.notna().mean() * 100, 1),
            "unique": _i(series.nunique()),
            "samples": [str(v) for v in series.dropna().unique()[:3]]
        })

    features_meta = {
        "registry": registry,
        "groups": list(dict.fromkeys(c["group"] for c in registry)),
        "n_inverters": n_inverters,
        "n_numeric": _i(df.select_dtypes(include="number").shape[1]),
        "n_categorical": _i(df.select_dtypes(exclude="number").shape[1]),
        "inverters_list": list(inverters)
    }

    # Descriptive Statistics
    desc_cols = ["DC_POWER", "AC_POWER", "DAILY_YIELD", "AMBIENT_TEMPERATURE", "MODULE_TEMPERATURE", "IRRADIATION", "EFFICIENCY", "TEMP_DIFF"]
    desc_overall = df[desc_cols].describe()
    desc_day = df[df["IS_DAY"]][desc_cols].describe()
    desc_night = df[~df["IS_DAY"]][desc_cols].describe()

    stats_table = []
    for col in desc_cols:
        stats_table.append({
            "name": col,
            "overall_mean": _f(desc_overall.loc["mean", col]),
            "overall_std": _f(desc_overall.loc["std", col]),
            "day_mean": _f(desc_day.loc["mean", col]),
            "day_max": _f(desc_day.loc["max", col]),
            "night_mean": _f(desc_night.loc["mean", col]),
            "overall_min": _f(desc_overall.loc["min", col]),
            "overall_max": _f(desc_overall.loc["max", col]),
        })

    # Inverters ranking
    inverter_stats = []
    inv_daily = df.groupby(["SOURCE_KEY", "DATE"])["DAILY_YIELD"].max().reset_index()
    median_plant_yield = float(inv_daily["DAILY_YIELD"].median())

    for inv in inverters:
        inv_data = df[df["SOURCE_KEY"] == inv]
        inv_yield = float(inv_data.groupby("DATE")["DAILY_YIELD"].max().mean())
        ipi = (inv_yield / median_plant_yield * 100) if median_plant_yield > 0 else 100.0

        inverter_stats.append({
            "inverter_id": inv,
            "avg_daily_yield": _f(inv_yield),
            "max_ac_kw": _f(inv_data["AC_POWER"].max()),
            "avg_day_ac_kw": _f(inv_data[inv_data["IS_DAY"]]["AC_POWER"].mean()),
            "avg_efficiency": _f(inv_data["EFFICIENCY"].dropna().mean()),
            "ipi": _f(ipi, 1),
            "status": "Healthy" if ipi >= 95 else ("Moderate Loss" if ipi >= 85 else "Fault / High Soiling")
        })

    inverter_stats.sort(key=lambda x: x["ipi"], reverse=True)

    # Hourly Diurnal Curve
    hourly = df.groupby("HOUR").agg({
        "DC_POWER": "mean",
        "AC_POWER": "mean",
        "IRRADIATION": "mean",
        "AMBIENT_TEMPERATURE": "mean",
        "MODULE_TEMPERATURE": "mean",
        "TEMP_DIFF": "mean"
    }).reset_index()

    diurnal = {
        "hours": hourly["HOUR"].tolist(),
        "dc_power": [_f(v) for v in hourly["DC_POWER"]],
        "ac_power": [_f(v) for v in hourly["AC_POWER"]],
        "irradiation": [_f(v * 1000, 1) for v in hourly["IRRADIATION"]],
        "ambient_temp": [_f(v) for v in hourly["AMBIENT_TEMPERATURE"]],
        "module_temp": [_f(v) for v in hourly["MODULE_TEMPERATURE"]],
    }

    # Histograms for Key Fields (Daylight filtered for AC/DC/Irrad)
    histograms = {}
    for col in DISTRIBUTION_COLS:
        subset = df[df["IS_DAY"]][col] if col in ("AC_POWER", "DC_POWER", "IRRADIATION", "EFFICIENCY") else df[col]
        histograms[col] = _histogram(subset)

    # Standardized Z-Score Histograms
    standardized = {}
    for col in STANDARDIZE_COLS:
        subset = df[df["IS_DAY"]][col]
        z = (subset - subset.mean()) / subset.std()
        standardized[col] = _histogram(z)

    # Correlation Matrix Heatmap
    corr_matrix = df[desc_cols].corr()
    matrix = []
    for r in desc_cols:
        row = []
        for c in desc_cols:
            val = corr_matrix.loc[r, c]
            v = None if pd.isna(val) else _f(val, 2)
            strong = v is not None and abs(v) >= 0.5
            row.append({"v": v, "color": _heat_color(v), "strong": strong})
        matrix.append(row)

    heatmap = {"labels": desc_cols, "matrix": matrix}

    # Influence on Target (AC_POWER)
    infl = corr_matrix[TARGET_COL].drop(TARGET_COL).sort_values(ascending=False)
    influence = {
        "labels": [str(c) for c in infl.index],
        "values": [_f(v, 2) for v in infl.values]
    }

    # Imputation lab benchmark (uses raw wth_df for honest benchmark)
    imputation_lab = evaluate_imputation_strategies(wth_df)

    # Build gap audit summary for template
    gap_summary = {
        "total_gaps": len(gap_audit),
        "spline_gaps": sum(1 for g in gap_audit if g["strategy"] == "Linear Spline"),
        "diurnal_gaps": sum(1 for g in gap_audit if g["strategy"] == "Diurnal Profile Matching"),
        "night_gaps": sum(1 for g in gap_audit if g["strategy"] == "Zero-Clamp (Night)"),
        "max_gap_min": max((g["duration_min"] for g in gap_audit), default=0),
        "total_imputed_slots": sum(g["n_slots"] for g in gap_audit),
        "events": gap_audit[:50],  # cap at 50 for template safety
    }

    return {
        "schema_ok": True,
        "plant_num": plant_num,
        "n_cols": len(df.columns),
        "overview": overview,
        "features": features_meta,
        "descriptive": stats_table,
        "inverters": inverter_stats,
        "diurnal": diurnal,
        "histograms": histograms,
        "standardized": standardized,
        "heatmap": heatmap,
        "influence": influence,
        "imputation_lab": imputation_lab,
        "gap_summary": gap_summary,
    }


def get_plant_bundle(plant_num=1, data_dir=None):
    key = (plant_num, data_dir)
    with _cache_lock:
        if key not in _bundle_cache:
            while len(_bundle_cache) >= _CACHE_MAX:
                _bundle_cache.popitem(last=False)
            _bundle_cache[key] = build_plant_bundle(plant_num, data_dir)
        else:
            _bundle_cache.move_to_end(key)
        return _bundle_cache[key]


def invalidate_cache():
    """Force re-computation of all bundles (call after data changes)."""
    with _cache_lock:
        _bundle_cache.clear()
