"""SolarSense Flask Application.

Integrates SCADA sensor exploration, imputation benchmark lab,
and machine learning power forecasting.
"""

import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

import eda
import model

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "solarsense-inverter-key-2026")

PIPELINE_STEPS = [
    {
        "id": "upload",
        "step": "01",
        "label": "Upload Dataset",
        "endpoint": "upload_dataset",
        "eyebrow": "Stage 01 · Intake",
        "live": True,
        "note": "Bring in raw solar generation and weather sensor SCADA files, or explore bundled Plant 1 and Plant 2.",
    },
    {
        "id": "features",
        "step": "02",
        "label": "Analyse Features",
        "endpoint": "features_registry",
        "eyebrow": "Stage 02 · Schema",
        "live": True,
        "note": "SCADA sensor channels, physical units, 15-minute sampling rates, and 22-inverter hardware registry.",
    },
    {
        "id": "descriptive",
        "step": "03",
        "label": "Descriptive Statistics",
        "endpoint": "descriptive_stats",
        "eyebrow": "Stage 03 · Statistics",
        "live": True,
        "note": "Distributional metrics comparing active daylight hours against nighttime cycles.",
    },
    {
        "id": "missing",
        "step": "04",
        "label": "Missing Value Analysis",
        "endpoint": "missing_values",
        "eyebrow": "Stage 04 · Imputation Lab",
        "live": True,
        "note": "Benchmark Forward Fill vs Linear Spline vs Diurnal Pattern matching on missing sensor intervals.",
    },
    {
        "id": "visualize",
        "step": "05",
        "label": "Data Visualization",
        "endpoint": "visualizations",
        "eyebrow": "Stage 05 · Visuals",
        "live": True,
        "note": "Diurnal generation profiles, thermal heatmaps, and Inverter Performance Index (IPI) degradation tracking.",
    },
    {
        "id": "preprocess",
        "step": "06",
        "label": "Preprocessing",
        "endpoint": "preprocessing",
        "eyebrow": "Stage 06 · Preprocessing",
        "live": True,
        "note": "Thermal differential engineering and strict chronological 80/20 train/test holdout split.",
    },
    {
        "id": "train",
        "step": "07",
        "label": "Model Training",
        "endpoint": "train_model",
        "eyebrow": "Stage 07 · Training",
        "live": True,
        "note": "Ridge linear baseline, Random Forest, and HistGradientBoosting regressors.",
    },
    {
        "id": "evaluate",
        "step": "08",
        "label": "Model Evaluation",
        "endpoint": "evaluate_model",
        "eyebrow": "Stage 08 · Evaluation",
        "live": True,
        "note": "Sealed temporal holdout test metrics (R², MAE, RMSE) and Gini feature attributions.",
    },
    {
        "id": "predict",
        "step": "09",
        "label": "Predict Generation",
        "endpoint": "predict_placement",
        "eyebrow": "Stage 09 · Inference",
        "live": True,
        "note": "Sub-hourly AC power forecasting with local physics-based explanations.",
    },
]


def _get_active_plant():
    return session.get("plant_num", 1)


def _step_pager(current_id):
    ids = [s["id"] for s in PIPELINE_STEPS]
    try:
        idx = ids.index(current_id)
        prev_step = PIPELINE_STEPS[idx - 1] if idx > 0 else None
        next_step = PIPELINE_STEPS[idx + 1] if idx < len(PIPELINE_STEPS) - 1 else None
        return prev_step, next_step
    except ValueError:
        return None, None


@app.context_processor
def inject_globals():
    return {
        "pipeline_steps": PIPELINE_STEPS,
        "plant_num": _get_active_plant()
    }


@app.route("/switch-plant/<int:num>")
def switch_plant(num):
    if num in (1, 2):
        session["plant_num"] = num
    referer = request.headers.get("Referer")
    if referer and "/switch-plant/" not in referer:
        return redirect(referer)
    return redirect(url_for("home"))


@app.route("/")
def home():
    plant_num = _get_active_plant()
    bundle = eda.get_plant_bundle(plant_num)
    return render_template(
        "index.html",
        bundle=bundle,
        active_step="overview"
    )


@app.route("/upload")
def upload_dataset():
    plant_num = _get_active_plant()
    bundle = eda.get_plant_bundle(plant_num)
    step = next(s for s in PIPELINE_STEPS if s["id"] == "upload")
    prev_step, next_step = _step_pager("upload")
    return render_template(
        "upload.html",
        bundle=bundle,
        step=step,
        active_step="upload",
        prev_step=prev_step,
        next_step=next_step
    )


@app.route("/features")
def features_registry():
    plant_num = _get_active_plant()
    bundle = eda.get_plant_bundle(plant_num)
    step = next(s for s in PIPELINE_STEPS if s["id"] == "features")
    prev_step, next_step = _step_pager("features")
    return render_template(
        "features.html",
        bundle=bundle,
        step=step,
        active_step="features",
        prev_step=prev_step,
        next_step=next_step
    )


@app.route("/descriptive")
def descriptive_stats():
    plant_num = _get_active_plant()
    bundle = eda.get_plant_bundle(plant_num)
    step = next(s for s in PIPELINE_STEPS if s["id"] == "descriptive")
    prev_step, next_step = _step_pager("descriptive")
    return render_template(
        "descriptive.html",
        bundle=bundle,
        step=step,
        active_step="descriptive",
        prev_step=prev_step,
        next_step=next_step
    )


@app.route("/missing")
def missing_values():
    plant_num = _get_active_plant()
    bundle = eda.get_plant_bundle(plant_num)
    step = next(s for s in PIPELINE_STEPS if s["id"] == "missing")
    prev_step, next_step = _step_pager("missing")
    return render_template(
        "missing.html",
        bundle=bundle,
        step=step,
        active_step="missing",
        prev_step=prev_step,
        next_step=next_step
    )


@app.route("/visualize")
def visualizations():
    plant_num = _get_active_plant()
    bundle = eda.get_plant_bundle(plant_num)
    step = next(s for s in PIPELINE_STEPS if s["id"] == "visualize")
    prev_step, next_step = _step_pager("visualize")
    return render_template(
        "visualize.html",
        bundle=bundle,
        step=step,
        active_step="visualize",
        prev_step=prev_step,
        next_step=next_step
    )


@app.route("/preprocess")
def preprocessing():
    plant_num = _get_active_plant()
    bundle = eda.get_plant_bundle(plant_num)
    step = next(s for s in PIPELINE_STEPS if s["id"] == "preprocess")
    prev_step, next_step = _step_pager("preprocess")
    return render_template(
        "preprocess.html",
        bundle=bundle,
        step=step,
        active_step="preprocess",
        prev_step=prev_step,
        next_step=next_step
    )


@app.route("/train")
def train_model():
    plant_num = _get_active_plant()
    bundle = eda.get_plant_bundle(plant_num)
    mb = model.get_model_bundle(plant_num)
    step = next(s for s in PIPELINE_STEPS if s["id"] == "train")
    prev_step, next_step = _step_pager("train")
    return render_template(
        "train.html",
        bundle=bundle,
        mb=mb,
        step=step,
        active_step="train",
        prev_step=prev_step,
        next_step=next_step
    )


@app.route("/evaluate")
def evaluate_model():
    plant_num = _get_active_plant()
    bundle = eda.get_plant_bundle(plant_num)
    mb = model.get_model_bundle(plant_num)
    step = next(s for s in PIPELINE_STEPS if s["id"] == "evaluate")
    prev_step, next_step = _step_pager("evaluate")
    return render_template(
        "evaluate.html",
        bundle=bundle,
        mb=mb,
        step=step,
        active_step="evaluate",
        prev_step=prev_step,
        next_step=next_step
    )


@app.route("/predict", methods=["GET", "POST"])
def predict_placement():
    plant_num = _get_active_plant()
    bundle = eda.get_plant_bundle(plant_num)
    mb = model.get_model_bundle(plant_num)
    step = next(s for s in PIPELINE_STEPS if s["id"] == "predict")
    prev_step, next_step = _step_pager("predict")

    result = None
    values = {}
    selected_model = mb["best"]

    if request.method == "POST":
        selected_model = request.form.get("model_name", mb["best"])
        for f in mb["form_meta"]:
            name = f["name"]
            raw_val = request.form.get(name, str(f["default"])).strip()
            try:
                values[name] = float(raw_val)
            except ValueError:
                values[name] = float(f["default"])

        result = model.predict(values, model_name=selected_model, plant_num=plant_num)

    return render_template(
        "predict.html",
        bundle=bundle,
        mb=mb,
        step=step,
        active_step="predict",
        prev_step=prev_step,
        next_step=next_step,
        result=result,
        values=values,
        selected_model=selected_model
    )


# ---------------------------------------------------------------------------
# JSON API Endpoints
# ---------------------------------------------------------------------------

@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json(silent=True) or {}
    plant_num = int(data.get("plant_num", _get_active_plant()))
    model_name = data.get("model_name")
    values = data.get("values", {})
    pred = model.predict(values, model_name=model_name, plant_num=plant_num)
    return jsonify(pred)


@app.route("/api/bundle")
def api_bundle():
    plant_num = _get_active_plant()
    return jsonify(eda.get_plant_bundle(plant_num))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
