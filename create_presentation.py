import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette: Deep Slate, Solar Amber, Pure White, Light Slate, Charcoal
C_BG_DARK = RGBColor(15, 23, 42)      # #0F172A
C_BG_LIGHT = RGBColor(248, 250, 252)  # #F8FAFC
C_CARD_BG = RGBColor(255, 255, 255)   # #FFFFFF
C_CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0
C_AMBER = RGBColor(217, 119, 6)       # #D97706
C_AMBER_LIGHT = RGBColor(254, 243, 199) # #FEF3C7
C_TEXT_DARK = RGBColor(15, 23, 42)    # #0F172A
C_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
C_TEXT_LIGHT = RGBColor(248, 250, 252) # #F8FAFC
C_ACCENT_BLUE = RGBColor(37, 99, 235)  # #2563EB
C_ACCENT_GREEN = RGBColor(16, 185, 129)# #10B981

def add_blank_slide(bg_color=C_BG_LIGHT):
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = bg_color
    bg.line.fill.background()
    return slide

def add_header(slide, kicker, title):
    # Kicker / Category
    kicker_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_k = kicker_box.text_frame
    tf_k.word_wrap = True
    tf_k.margin_left = tf_k.margin_top = tf_k.margin_right = tf_k.margin_bottom = 0
    p_k = tf_k.paragraphs[0]
    p_k.text = kicker.upper()
    p_k.font.size = Pt(11)
    p_k.font.bold = True
    p_k.font.color.rgb = C_AMBER
    p_k.font.name = "Segoe UI"

    # Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.65))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_DARK
    p_t.font.name = "Segoe UI"

    # Subtle divider rule
    rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.02))
    rule.fill.solid()
    rule.fill.fore_color.rgb = C_CARD_BORDER
    rule.line.fill.background()

def create_card(slide, left, top, width, height, title="", title_color=C_TEXT_DARK, bg_color=C_CARD_BG, border_color=C_CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)

    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.18), width - Inches(0.4), Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = title_color
        p.font.name = "Segoe UI"
    return shape

# ==============================================================================
# SLIDE 1: Title Slide (Hero Dark Theme)
# ==============================================================================
s1 = add_blank_slide(bg_color=C_BG_DARK)

# Title & Subtitle container
t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(3.2))
tf1 = t_box.text_frame
tf1.word_wrap = True

p_k1 = tf1.paragraphs[0]
p_k1.text = "MACHINE LEARNING CAPSTONE PROJECT"
p_k1.font.size = Pt(13)
p_k1.font.bold = True
p_k1.font.color.rgb = C_AMBER
p_k1.font.name = "Segoe UI"

p_t1 = tf1.add_paragraph()
p_t1.text = "SolarSense: SCADA Telemetry Intelligence &\nMachine Learning Power Forecasting"
p_t1.font.size = Pt(36)
p_t1.font.bold = True
p_t1.font.color.rgb = C_TEXT_LIGHT
p_t1.font.name = "Segoe UI"
p_t1.space_before = Pt(14)

p_desc = tf1.add_paragraph()
p_desc.text = "End-to-end solar data engineering, 3-tier imputation, unsupervised anomaly diagnostics, and high-accuracy supervised forecasting across 136,000+ utility SCADA telemetry records."
p_desc.font.size = Pt(15)
p_desc.font.color.rgb = RGBColor(148, 163, 184)
p_desc.font.name = "Segoe UI"
p_desc.space_before = Pt(16)

# Meta info card at bottom
meta_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.3), Inches(11.3), Inches(1.3))
meta_card.fill.solid()
meta_card.fill.fore_color.rgb = RGBColor(30, 41, 59)
meta_card.line.color.rgb = RGBColor(51, 65, 85)
meta_card.line.width = Pt(1)

meta_tb = s1.shapes.add_textbox(Inches(1.3), Inches(5.5), Inches(10.7), Inches(0.9))
mtf = meta_tb.text_frame
mtf.word_wrap = True
mp = mtf.paragraphs[0]
mp.text = "PROJECT METRICS & SCOPE"
mp.font.size = Pt(10)
mp.font.bold = True
mp.font.color.rgb = C_AMBER
mp.font.name = "Segoe UI"

mp2 = mtf.add_paragraph()
mp2.text = "• Telemetry Records: 136,472 | Inverter Units: 22 Strings | Solar Plants: 2 Facilities | Observation: 34 Days (15-min Intervals)\n• Supervised Models: Linear Regression, Logistic Regression, Decision Tree, Random Forest, HistGradientBoosting\n• Unsupervised Models: K-Means Clustering, DBSCAN Outlier Detection, Isolation Forest Anomaly Detection"
mp2.font.size = Pt(11.5)
mp2.font.color.rgb = RGBColor(226, 232, 240)
mp2.font.name = "Segoe UI"
mp2.space_before = Pt(4)

# ==============================================================================
# SLIDE 2: 0. ABSTRACT OF THE PROJECT (8-10 Points)
# ==============================================================================
s2 = add_blank_slide()
add_header(s2, "0. Abstract of the Project", "Core Objectives, Methodology & Technical Contributions")

# 2 Columns of cards (Left: 5 points, Right: 5 points)
left_box = s2.shapes.add_textbox(Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.3))
tf2_l = left_box.text_frame
tf2_l.word_wrap = True

abstract_points_left = [
    ("1. Utility-Scale SCADA Ingestion", "Ingested 136,472 continuous telemetry records from two utility-scale solar farms across 34 days at synchronized 15-minute intervals."),
    ("2. Multi-Rate Sensor Gap Challenge", "Identified that weather stations exhibit non-uniform sensor dropouts (e.g., 82 missing slots in Plant 1) that cause significant modeling bias if filled naively."),
    ("3. Physics-Validated 3-Tier Imputation", "Engineered a 3-tier imputation protocol: Time Linear Splines for short gaps (RMSE 0.108 kW/m²), Diurnal Matching for prolonged outages, and Nocturnal Zero-Clamping."),
    ("4. Cross-Plant Electrical Calibration", "Diagnosed and resolved a 10× raw scaling artifact in Plant 1 direct current (DC), reconciling baseline inverter efficiency to an industry-standard 97.72%."),
    ("5. Dimensionality Reduction via PCA", "Applied Principal Component Analysis (PCA) to decouple correlated atmospheric metrics; demonstrated top 3 PCs retain 96.17% of total variance.")
]

for title, desc in abstract_points_left:
    p1 = tf2_l.add_paragraph() if tf2_l.paragraphs[0].text else tf2_l.paragraphs[0]
    p1.text = title
    p1.font.bold = True
    p1.font.size = Pt(12)
    p1.font.color.rgb = C_AMBER
    p1.font.name = "Segoe UI"
    p1.space_before = Pt(8)

    p2 = tf2_l.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_TEXT_DARK
    p2.font.name = "Segoe UI"

right_box = s2.shapes.add_textbox(Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.3))
tf2_r = right_box.text_frame
tf2_r.word_wrap = True

abstract_points_right = [
    ("6. Unsupervised Clustering & DBSCAN", "Employed K-Means to identify 3 operational generation regimes and DBSCAN (4.4% density outliers) to isolate transient sensor drift and grid disconnection spikes."),
    ("7. Remote Anomaly Detection (IPI)", "Formulated the Inverter Performance Index (IPI) and Isolation Forest (3.47% anomalies) to autonomously pinpoint degraded inverter bvBOhCHirYxfHG8 (-15% yield deficit)."),
    ("8. Multi-Model Supervised Classification", "Benchmarked Logistic Regression, Decision Trees, and Random Forests for operational state classification, reaching 98.01% 5-fold cross-validation accuracy."),
    ("9. High-Accuracy Sub-Hourly Forecasting", "Trained HistGradientBoosting for AC power regression, achieving Holdout R² = 0.9625, MAE = 28.77 kW, and Daylight MAPE = 9.1% with zero future temporal leakage."),
    ("10. Full-Stack Deployed System", "Packaged the entire pipeline into an interactive 9-stage web platform with live physics-based attribution explanations, exportable API, and full audit logs.")
]

for title, desc in abstract_points_right:
    p1 = tf2_r.add_paragraph() if tf2_r.paragraphs[0].text else tf2_r.paragraphs[0]
    p1.text = title
    p1.font.bold = True
    p1.font.size = Pt(12)
    p1.font.color.rgb = C_ACCENT_BLUE
    p1.font.name = "Segoe UI"
    p1.space_before = Pt(8)

    p2 = tf2_r.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_TEXT_DARK
    p2.font.name = "Segoe UI"

# ==============================================================================
# SLIDE 3: 1. DATASET
# ==============================================================================
s3 = add_blank_slide()
add_header(s3, "1. Dataset", "Multi-Plant SCADA Telemetry Architecture & Sensor Channel Schema")

# 3 Metric Cards at Top
metrics_data = [
    ("136,472", "Total SCADA Records", "Plant 1: 68,778 | Plant 2: 67,698", C_AMBER),
    ("22 Strings", "Monitored Inverters", "Independent string inverters per solar farm", C_ACCENT_BLUE),
    ("15-Min", "Telemetry Granularity", "34 continuous observation days (May–June 2020)", C_ACCENT_GREEN)
]

for i, (val, label, sub, color) in enumerate(metrics_data):
    left = Inches(0.8 + i * 4.0)
    create_card(s3, left, Inches(1.65), Inches(3.7), Inches(1.4))
    tb = s3.shapes.add_textbox(left + Inches(0.2), Inches(1.75), Inches(3.3), Inches(1.1))
    tf = tb.text_frame
    tf.margin_top = tf.margin_left = tf.margin_bottom = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.text = val
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = color
    p.font.name = "Segoe UI"
    
    p2 = tf.add_paragraph()
    p2.text = label
    p2.font.size = Pt(12)
    p2.font.bold = True
    p2.font.color.rgb = C_TEXT_DARK
    
    p3 = tf.add_paragraph()
    p3.text = sub
    p3.font.size = Pt(9.5)
    p3.font.color.rgb = C_TEXT_MUTED

# Table / Schema Card Below
create_card(s3, Inches(0.8), Inches(3.25), Inches(11.733), Inches(3.8), title="Primary Sensor Channels & Engineering Roles")

schema_box = s3.shapes.add_textbox(Inches(1.0), Inches(3.75), Inches(11.3), Inches(3.1))
stf = schema_box.text_frame
stf.word_wrap = True

table_rows = [
    ("DATE_TIME & PLANT_ID", "Temporal / Identity", "YYYY-MM-DD HH:MM | 4135001 (Plant 1) & 4136001 (Plant 2)", "Master synchronization key across multi-rate generation & weather data."),
    ("DC_POWER (kW)", "Electrical Input", "Direct current from string PV panels (0 to 1,447 kW calibrated)", "Raw photovoltaic input power fed into string inverters."),
    ("AC_POWER (kW)", "Electrical Output", "Alternating current delivered to grid (0 to 1,410 kW peak)", "Primary supervised regression target for grid dispatch scheduling."),
    ("DAILY_YIELD & TOTAL_YIELD (kWh)", "Energy Meters", "Daily generation counter (resets midnight) & lifetime energy counter", "Used to compute cumulative energy and Inverter Performance Index (IPI)."),
    ("IRRADIATION (kW/m²)", "Meteorological", "Global Horizontal Irradiance (GHI) from weather station pyranometer", "Primary physical driver of generation (r = 0.97 with AC power output)."),
    ("MODULE_TEMP & AMBIENT_TEMP (°C)", "Thermal Telemetry", "Panel surface thermocouple (up to 65.5°C) & ambient air temperature", "Drives non-linear silicon thermal derating (~0.4%/°C power loss above 25°C)."),
    ("TEMP_DIFF (ΔT = T_mod - T_amb)", "Engineered Physics", "Thermal gradient capturing solar absorption and wind heat dissipation", "Key derived predictor isolating cell heating stress from irradiance.")
]

for ch, cat, spec, role in table_rows:
    p = stf.add_paragraph() if stf.paragraphs[0].text else stf.paragraphs[0]
    p.text = f"• {ch}  [{cat}]:  {role}"
    p.font.size = Pt(10.5)
    p.font.name = "Segoe UI"
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(4)

# ==============================================================================
# SLIDE 4: 2. EXPLORATORY DATA ANALYSIS (EDA)
# ==============================================================================
s4 = add_blank_slide()
add_header(s4, "2. Exploratory Data Analysis (EDA)", "Diurnal Decomposition, Electrical Calibration & Thermal Correlation")

# 4 Cards Layout
eda_cards = [
    ("Instrumentation Scale Normalization", 
     "• Discovery: Plant 1 DC power was recorded on a 10× electrical scale (mean daylight DC = 3,147 kW vs AC = 307.8 kW), superficially showing an impossible 9.7% efficiency.\n• Fix: Dividing Plant 1 DC by 10 restored physical parity.\n• Baseline Result: Both plants exhibit identical, healthy inverter conversion efficiency of 97.72% (AC / DC).", 
     C_AMBER),
    ("Diurnal Cycle & Day/Night Split", 
     "• Physical Zero Boundary: Nocturnal generation (18:30 to 05:30) is physically zero with minor electronic resting jitter (-0.001 kW).\n• Eliminating Zero-Inflation: Segregated active daylight hours (IS_DAY) from nocturnal intervals.\n• Preventing R² Distortion: Modeling daylight exclusively prevents artificially inflated scores caused by trivial night zeros.", 
     C_ACCENT_BLUE),
    ("Thermal Saturation & Derating", 
     "• Module temperatures peak at 65.55°C during summer afternoons.\n• Negative Temperature Coefficient: Crystalline silicon suffers power derating of ~0.4%/°C above 25°C.\n• Thermal Gradient: Module temperature exceeds ambient temperature by up to 35.2°C at peak solar noon, creating significant efficiency drops.", 
     C_TEXT_DARK),
    ("Feature Correlation Hierarchy", 
     "• AC Power Target Correlation (Pearson r):\n   - IRRADIATION: r = +0.97 (dominant linear driver)\n   - DC POWER: r = +0.99 (direct electrical relationship)\n   - MODULE TEMP: r = +0.81 (strong daytime collinearity)\n   - TEMP DIFF (ΔT): r = +0.76 (thermal absorption proxy)\n   - AMBIENT TEMP: r = +0.54 (seasonal baseline)", 
     C_ACCENT_GREEN)
]

for i, (title, content, color) in enumerate(eda_cards):
    r = i // 2
    c = i % 2
    left = Inches(0.8 + c * 6.0)
    top = Inches(1.65 + r * 2.7)
    create_card(s4, left, top, Inches(5.7), Inches(2.5), title=title, title_color=color)
    tb = s4.shapes.add_textbox(left + Inches(0.2), top + Inches(0.6), Inches(5.3), Inches(1.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = content
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_TEXT_DARK
    p.font.name = "Segoe UI"

# ==============================================================================
# SLIDE 5: 3. MISSING VALUES IDENTIFICATION AND REPLACEMENT
# ==============================================================================
s5 = add_blank_slide()
add_header(s5, "3. Missing Values Identification & Replacement", "3-Tier Physics Imputation Engine & Ground-Truth Reconstruction Benchmark")

# Left: The Problem & 3-Tier Policy
create_card(s5, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.3), title="The Irregular Gap Problem & 3-Tier Policy")
tb5_l = s5.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.6))
tf5_l = tb5_l.text_frame
tf5_l.word_wrap = True

p = tf5_l.paragraphs[0]
p.text = "Why Static Standard Imputation Fails:"
p.font.bold = True
p.font.size = Pt(12)
p.font.color.rgb = C_AMBER

p2 = tf5_l.add_paragraph()
p2.text = "• Telemetry drops are non-uniform across days (e.g. 82 missing 15-min intervals in Plant 1, 5 in Plant 2) caused by gateway resets and network timeouts.\n• Forward Fill (LOCF) Failure: Carrying forward a 12:00 PM peak (1.0 kW/m²) across a 2-hour cloudy dropout overestimates solar power by >200%.\n• Mean Fill Failure: Imputing daytime mean ignores solar zenith elevation angles."
p2.font.size = Pt(11)
p2.space_before = Pt(4)

p3 = tf5_l.add_paragraph()
p3.text = "The SolarSense 3-Tier Imputation Policy:"
p3.font.bold = True
p3.font.size = Pt(12)
p3.font.color.rgb = C_ACCENT_BLUE
p3.space_before = Pt(10)

p4 = tf5_l.add_paragraph()
p4.text = "1. Nocturnal Gaps (18:30–05:30): Physical Zero-Clamp (Irradiation = 0.0 kW/m²; clips electronic resting noise).\n2. Short Daytime Gaps (≤ 1 Hour): Time Linear Spline Interpolation (captures transient cloud trajectory accurately).\n3. Prolonged Daytime Outages (> 1 Hour): Diurnal Profile Matching (imputes historical same-hour solar elevation mean)."
p4.font.size = Pt(11)
p4.space_before = Pt(4)

# Right: Benchmark Evaluation Table
create_card(s5, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.3), title="Imputation Benchmark (10% Ground-Truth Dropout)")
tb5_r = s5.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.6))
tf5_r = tb5_r.text_frame
tf5_r.word_wrap = True

p_bench = tf5_r.paragraphs[0]
p_bench.text = "Tested against real ground truth records (N=3,182) to mathematically validate reconstruction accuracy:"
p_bench.font.size = Pt(11)

benchmark_metrics = [
    ("Solar Irradiance (G, kW/m²)", [
        ("Forward Fill (LOCF)", "MAE 0.092 | RMSE 0.130"),
        ("Diurnal Profile Matching", "MAE 0.126 | RMSE 0.165"),
        ("Time Linear Spline (Winner)", "MAE 0.067 | RMSE 0.108  [Best]")
    ]),
    ("Module Temperature (T_mod, °C)", [
        ("Forward Fill (LOCF)", "MAE 2.92°C | RMSE 4.10°C"),
        ("Diurnal Profile Matching", "MAE 4.75°C | RMSE 6.11°C"),
        ("Time Linear Spline (Winner)", "MAE 1.65°C | RMSE 2.37°C  [Best]")
    ]),
    ("Ambient Temperature (T_amb, °C)", [
        ("Forward Fill (LOCF)", "MAE 1.21°C | RMSE 1.84°C"),
        ("Time Linear Spline (Winner)", "MAE 0.65°C | RMSE 0.98°C  [Best]")
    ])
]

for sensor, strats in benchmark_metrics:
    p_s = tf5_r.add_paragraph()
    p_s.text = f"• {sensor}:"
    p_s.font.bold = True
    p_s.font.size = Pt(11)
    p_s.font.color.rgb = C_TEXT_DARK
    p_s.space_before = Pt(8)
    for s_name, s_val in strats:
        p_v = tf5_r.add_paragraph()
        p_v.text = f"   - {s_name}: {s_val}"
        p_v.font.size = Pt(10)
        p_v.font.color.rgb = C_AMBER if "[Best]" in s_val else C_TEXT_MUTED

# ==============================================================================
# SLIDE 6: 4. PCA - IDENTIFICATION OF FEATURES FOR MODELING
# ==============================================================================
s6 = add_blank_slide()
add_header(s6, "4. Principal Component Analysis (PCA)", "Feature Dimensionality Reduction, Eigenvalues & Variance Decomposition")

# 3 Cards Layout: Variance Explained, Component Interpretation, Modeling Impact
create_card(s6, Inches(0.8), Inches(1.65), Inches(3.7), Inches(5.3), title="Explained Variance Ratio")
tb6_1 = s6.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(3.3), Inches(4.5))
tf6_1 = tb6_1.text_frame
tf6_1.word_wrap = True

tf6_1.paragraphs[0].text = "Eigenvalue & Variance Distribution:"
tf6_1.paragraphs[0].font.bold = True
tf6_1.paragraphs[0].font.size = Pt(11)

pca_var_text = [
    ("PC1 (Primary Solar Flux)", "57.62%", "Captures primary solar irradiance and panel surface temperature."),
    ("PC2 (Thermal Gradient)", "21.92%", "Captures ambient heating and module thermal delta (ΔT)."),
    ("PC3 (Diurnal Solar Angle)", "16.62%", "Encodes diurnal hour-of-day solar elevation arc."),
    ("PC4 (Sub-Interval Cadence)", "3.12%", "Minor 15-minute sampling adjustments."),
    ("PC5 & PC6 (Residual Noise)", "0.72%", "Insignificant atmospheric noise.")
]

for pc, pct, expl in pca_var_text:
    p = tf6_1.add_paragraph()
    p.text = f"{pc}: {pct}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = C_AMBER if "PC1" in pc or "PC2" in pc or "PC3" in pc else C_TEXT_MUTED
    p.space_before = Pt(6)
    p_sub = tf6_1.add_paragraph()
    p_sub.text = expl
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = C_TEXT_DARK

create_card(s6, Inches(4.8), Inches(1.65), Inches(3.7), Inches(5.3), title="Cumulative Variance Retained")
tb6_2 = s6.shapes.add_textbox(Inches(5.0), Inches(2.2), Inches(3.3), Inches(4.5))
tf6_2 = tb6_2.text_frame
tf6_2.word_wrap = True

tf6_2.paragraphs[0].text = "Dimensionality Threshold:"
tf6_2.paragraphs[0].font.bold = True
tf6_2.paragraphs[0].font.size = Pt(11)

cum_text = [
    ("Top 1 Component (PC1)", "57.62% Total Information"),
    ("Top 2 Components (PC1-2)", "79.54% Total Information"),
    ("Top 3 Components (PC1-3)", "96.17% Total Information  [OPTIMAL]"),
    ("Top 4 Components (PC1-4)", "99.29% Total Information")
]

for comp, stat in cum_text:
    p = tf6_2.add_paragraph()
    p.text = comp
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(8)
    p_s = tf6_2.add_paragraph()
    p_s.text = stat
    p_s.font.size = Pt(10.5)
    p_s.font.color.rgb = C_ACCENT_GREEN if "[OPTIMAL]" in stat else C_TEXT_MUTED

p_c = tf6_2.add_paragraph()
p_c.text = "Key Takeaway:\nCompressing 6 continuous physical dimensions into 3 principal components retains >96% of variance while eliminating multi-collinearity between ambient temperature and module surface temperature."
p_c.font.size = Pt(10)
p_c.font.color.rgb = C_TEXT_DARK
p_c.space_before = Pt(14)

create_card(s6, Inches(8.8), Inches(1.65), Inches(3.733), Inches(5.3), title="Component Loadings for Modeling")
tb6_3 = s6.shapes.add_textbox(Inches(9.0), Inches(2.2), Inches(3.3), Inches(4.5))
tf6_3 = tb6_3.text_frame
tf6_3.word_wrap = True

tf6_3.paragraphs[0].text = "Physical Feature Loadings:"
tf6_3.paragraphs[0].font.bold = True
tf6_3.paragraphs[0].font.size = Pt(11)

loadings = [
    ("IRRADIATION", "+0.54 on PC1", "Dominant positive driver for solar power generation."),
    ("MODULE_TEMPERATURE", "+0.51 on PC1", "Correlates with direct sunlight exposure."),
    ("TEMP_DIFF (ΔT)", "+0.62 on PC2", "Isolates cell heating stress from ambient air."),
    ("AMBIENT_TEMPERATURE", "+0.58 on PC2", "Captures thermal background context."),
    ("HOUR (Solar Angle)", "+0.71 on PC3", "Governs diurnal sunrise-to-sunset trajectory.")
]

for feat, load, role in loadings:
    p = tf6_3.add_paragraph()
    p.text = f"• {feat} ({load}):"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_ACCENT_BLUE
    p.space_before = Pt(6)
    p_r = tf6_3.add_paragraph()
    p_r.text = role
    p_r.font.size = Pt(9.5)
    p_r.font.color.rgb = C_TEXT_DARK

# ==============================================================================
# SLIDE 7: 5. MACHINE LEARNING MODELS - SUPERVISED
# ==============================================================================
s7 = add_blank_slide()
add_header(s7, "5. Machine Learning Models — Supervised", "Linear Regression, Logistic Classification & Decision Tree Ensembles")

# 3 Columns for 3 Supervised paradigms
sup_models = [
    ("1. Linear & Ridge Regression", 
     "Continuous Power Output Regression", 
     C_AMBER,
     "• Inductive Bias: Closed-form L2-regularized linear response (alpha=1.0).\n• Role: Benchmark baseline & zero-cost interpretability surrogate.\n• Holdout Metrics:\n   - R² Score: 0.8741\n   - MAE: 46.23 kW\n   - RMSE: 68.54 kW\n• Linear Attribution: Exports beta coefficients on z-scored features for instantaneous runtime explanations (+/- kW contribution)."),
    
    ("2. Logistic Regression", 
     "Operational State & Threshold Classification", 
     C_ACCENT_BLUE,
     "• Inductive Bias: Sigmoidal linear log-odds decision boundary.\n• Classification Target: High-Output vs Normal Generation Regime (> median power threshold).\n• Holdout Metrics:\n   - Accuracy: 96.25%\n   - Precision: 97.77%\n   - Recall: 94.64%\n   - F1-Score: 96.18%\n• Rapid inference with guaranteed convergence in <0.05s."),
    
    ("3. Tree Ensembles (DT, RF, HistGB)", 
     "Non-Linear Saturation & Boosting Champion", 
     C_ACCENT_GREEN,
     "• Decision Tree: Max depth 6; Accuracy 96.53%, F1 96.48%.\n• Random Forest: 100 decorrelated bagged trees; Accuracy 96.50%, F1 96.44%.\n• HistGradientBoosting (Champion Regressor):\n   - Holdout R² Score: 0.9625\n   - MAE: 28.77 kW\n   - Daylight MAPE: 9.1%\n   - Training Latency: 0.62 seconds\n• Captures non-linear thermal derating and clipping.")
]

for i, (title, sub, color, desc) in enumerate(sup_models):
    left = Inches(0.8 + i * 4.0)
    create_card(s7, left, Inches(1.65), Inches(3.7), Inches(5.3), title=title, title_color=color)
    tb = s7.shapes.add_textbox(left + Inches(0.2), Inches(2.2), Inches(3.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_sub = tf.paragraphs[0]
    p_sub.text = sub
    p_sub.font.bold = True
    p_sub.font.size = Pt(10.5)
    p_sub.font.color.rgb = C_TEXT_MUTED
    
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(10.5)
    p_desc.font.color.rgb = C_TEXT_DARK
    p_desc.space_before = Pt(8)

# ==============================================================================
# SLIDE 8: 5. MACHINE LEARNING MODELS - UNSUPERVISED
# ==============================================================================
s8 = add_blank_slide()
add_header(s8, "5. Machine Learning Models — Unsupervised", "Clustering Generation Regimes, DBSCAN Outlier Detection & Anomaly Diagnostics")

unsup_models = [
    ("1. K-Means Clustering", 
     "Diurnal Generation Regimes (k=3)", 
     C_AMBER,
     "• Purpose: Partition continuous SCADA telemetry into distinct operational regimes without human labels.\n• Cluster 0 (Morning Ramp / Evening Cooldown):\n   - 9,863 intervals (low sun elevation, cool ambient air).\n• Cluster 1 (Peak Midday / Solar Saturation):\n   - 19,298 intervals (G > 0.6 kW/m², high module heating).\n• Cluster 2 (Diffuse Light / Cloudy Monsoon Regime):\n   - 9,467 intervals (moderate temperature, low irradiance)."),
    
    ("2. DBSCAN Density Clustering", 
     "Sensor Drift & Communication Noise Filtering", 
     C_ACCENT_BLUE,
     "• Parameters: eps = 0.8, min_samples = 25 on standardized multi-sensor space.\n• Core Result: Successfully isolated 220 density outliers (4.4% of sampled telemetry).\n• Physical Interpretation:\n   - Identifies non-physical sensor spikes (e.g. sudden thermocouple drops).\n   - Flags inverter tripping events where irradiance is peak (1.1 kW/m²) but AC power instantly drops to 0 kW."),
    
    ("3. Isolation Forest & IPI", 
     "Inverter Degradation & Hardware Fault Detection", 
     C_ACCENT_GREEN,
     "• Contamination Rate: Set to 3.5% (identifying 1,341 anomalous SCADA rows across fleet).\n• Inverter Performance Index (IPI):\n   IPI_i = (E_daily,i / Median(E_daily)) * 100%\n• Hardware Diagnostic Outcome:\n   - 21 inverters operate healthy (98.5% - 104.2% IPI).\n   - Inverter 'bvBOhCHirYxfHG8' detected at 88.3% IPI with recurring 12-15% midday deficit -> isolates panel soiling and string faults remotely!")
]

for i, (title, sub, color, desc) in enumerate(unsup_models):
    left = Inches(0.8 + i * 4.0)
    create_card(s8, left, Inches(1.65), Inches(3.7), Inches(5.3), title=title, title_color=color)
    tb = s8.shapes.add_textbox(left + Inches(0.2), Inches(2.2), Inches(3.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_sub = tf.paragraphs[0]
    p_sub.text = sub
    p_sub.font.bold = True
    p_sub.font.size = Pt(10.5)
    p_sub.font.color.rgb = C_TEXT_MUTED
    
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(10.5)
    p_desc.font.color.rgb = C_TEXT_DARK
    p_desc.space_before = Pt(8)

# ==============================================================================
# SLIDE 9: 6. MODEL ACCURACY & EVALUATION METRICS
# ==============================================================================
s9 = add_blank_slide()
add_header(s9, "6. Model Accuracy & Evaluation Metrics", "Confusion Matrix, Precision, Recall, F1-Score & Regression Error Metrics")

# Left Card: Confusion Matrix Breakdown
create_card(s9, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.3), title="Supervised Classification: Confusion Matrix & Metrics")
tb9_l = s9.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf9_l = tb9_l.text_frame
tf9_l.word_wrap = True

tf9_l.paragraphs[0].text = "Sealed Holdout Classification (Test Rows: 7,726):"
tf9_l.paragraphs[0].font.bold = True
tf9_l.paragraphs[0].font.size = Pt(11)

clf_table = [
    ("Random Forest Classifier (Top Performer):", [
        ("True Negatives (TN)", "3,812 (Correct Normal State)"),
        ("False Positives (FP)", "73 (Type I Error)"),
        ("False Negatives (FN)", "196 (Type II Error)"),
        ("True Positives (TP)", "3,645 (Correct High State)")
    ]),
    ("Model Accuracy Metrics Comparison:", [
        ("Accuracy", "Logistic: 96.25% | DT: 96.53% | RF: 96.50%"),
        ("Precision", "Logistic: 0.9777 | DT: 0.9778 | RF: 0.9804"),
        ("Recall", "Logistic: 0.9464 | DT: 0.9521 | RF: 0.9490"),
        ("F1-Score", "Logistic: 0.9618 | DT: 0.9648 | RF: 0.9644")
    ])
]

for section, items in clf_table:
    p_sec = tf9_l.add_paragraph()
    p_sec.text = section
    p_sec.font.bold = True
    p_sec.font.size = Pt(11)
    p_sec.font.color.rgb = C_AMBER
    p_sec.space_before = Pt(8)
    for k, v in items:
        p_item = tf9_l.add_paragraph()
        p_item.text = f"• {k}: {v}"
        p_item.font.size = Pt(10)
        p_item.font.color.rgb = C_TEXT_DARK

# Right Card: Supervised Regression Sealed Holdout
create_card(s9, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.3), title="Supervised Regression: Sealed Holdout Forecasting")
tb9_r = s9.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf9_r = tb9_r.text_frame
tf9_r.word_wrap = True

tf9_r.paragraphs[0].text = "Continuous AC Power Forecasting Evaluation (kW):"
tf9_r.paragraphs[0].font.bold = True
tf9_r.paragraphs[0].font.size = Pt(11)

reg_models_data = [
    ("Ridge Regression (Linear Baseline)", "R² = 0.8741", "MAE: 46.23 kW | RMSE: 68.54 kW | MAPE: 18.2%", C_TEXT_MUTED),
    ("Random Forest (100 Trees)", "R² = 0.9571", "MAE: 29.85 kW | RMSE: 41.17 kW | MAPE: 9.8%", C_ACCENT_BLUE),
    ("HistGradientBoosting (Champion)", "R² = 0.9625", "MAE: 28.77 kW | RMSE: 38.93 kW | MAPE: 9.1%", C_ACCENT_GREEN)
]

for name, r2, err, color in reg_models_data:
    p_m = tf9_r.add_paragraph()
    p_m.text = f"{name}  ->  {r2}"
    p_m.font.bold = True
    p_m.font.size = Pt(11.5)
    p_m.font.color.rgb = color
    p_m.space_before = Pt(10)
    p_e = tf9_r.add_paragraph()
    p_e.text = err
    p_e.font.size = Pt(10.5)
    p_e.font.color.rgb = C_TEXT_DARK

p_why = tf9_r.add_paragraph()
p_why.text = "Why HistGradientBoosting is the Champion:\n• Lowest absolute error (MAE 28.77 kW, only ~9.2% of peak output).\n• Accurately models non-linear photovoltaic thermal saturation.\n• Sub-second training latency (0.62s vs 8.42s for Random Forest)."
p_why.font.size = Pt(10)
p_why.font.color.rgb = C_TEXT_DARK
p_why.space_before = Pt(12)

# ==============================================================================
# SLIDE 10: 7. CROSS VALIDATION 5 FOLD
# ==============================================================================
s10 = add_blank_slide()
add_header(s10, "7. Cross Validation 5-Fold", "5-Fold Stratified Validation Protocol, Stability Auditing & Zero-Leakage Split")

create_card(s10, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.3), title="5-Fold Cross Validation Results")
tb10_l = s10.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf10_l = tb10_l.text_frame
tf10_l.word_wrap = True

tf10_l.paragraphs[0].text = "5-Fold Stratified CV Generalization (Full Dataset):"
tf10_l.paragraphs[0].font.bold = True
tf10_l.paragraphs[0].font.size = Pt(11)

cv_results = [
    ("Random Forest Classifier", "Mean CV Accuracy: 98.01%  (± 0.08%)", "Highest stability across all 5 folds; minimal variance confirms zero overfitting."),
    ("Decision Tree Classifier", "Mean CV Accuracy: 97.90%  (± 0.05%)", "Tight standard deviation (0.05%) demonstrates robust threshold stability."),
    ("Logistic Regression Baseline", "Mean CV Accuracy: 97.38%  (± 0.10%)", "Strong linear separation threshold; converges reliably across all validation subsets.")
]

for model, acc, note in cv_results:
    p = tf10_l.add_paragraph()
    p.text = f"• {model}:"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = C_AMBER
    p.space_before = Pt(8)
    p_a = tf10_l.add_paragraph()
    p_a.text = acc
    p_a.font.bold = True
    p_a.font.size = Pt(10.5)
    p_a.font.color.rgb = C_ACCENT_GREEN
    p_n = tf10_l.add_paragraph()
    p_n.text = note
    p_n.font.size = Pt(9.5)
    p_n.font.color.rgb = C_TEXT_DARK

create_card(s10, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.3), title="Chronological Validation vs Random Shuffle")
tb10_r = s10.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf10_r = tb10_r.text_frame
tf10_r.word_wrap = True

tf10_r.paragraphs[0].text = "The Time-Series Validation Dilemma:"
tf10_r.paragraphs[0].font.bold = True
tf10_r.paragraphs[0].font.size = Pt(11)

time_series_points = [
    ("1. The Flaw of Standard K-Fold in Time Series", "Randomly shuffling time-series records causes future telemetry to leak into past training folds, creating artificially inflated metrics."),
    ("2. Strict Chronological Holdout Protocol", "Enforced an 80/20 chronological partition: the earliest 80% past records train models; the latest 20% future records serve as a sealed holdout."),
    ("3. Zero Preprocessing Leakage", "All imputations, scalers, and normalizations are fitted train-only; test records are evaluated exactly once."),
    ("4. Operational Significance for Grid Dispatch", "Guarantees that the reported R² = 0.9625 represents true day-ahead generalization capability for grid operators and utility dispatchers.")
]

for title, expl in time_series_points:
    p = tf10_r.add_paragraph()
    p.text = title
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_ACCENT_BLUE
    p.space_before = Pt(6)
    p_e = tf10_r.add_paragraph()
    p_e.text = expl
    p_e.font.size = Pt(9.5)
    p_e.font.color.rgb = C_TEXT_DARK

# ==============================================================================
# SLIDE 11: FULL STACK DEPLOYMENT & SUMMARY
# ==============================================================================
s11 = add_blank_slide(bg_color=C_BG_DARK)

t_box11 = s11.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.3), Inches(1.0))
tf11 = t_box11.text_frame
tf11.paragraphs[0].text = "DEPLOYMENT & CONCLUSION"
tf11.paragraphs[0].font.size = Pt(11)
tf11.paragraphs[0].font.bold = True
tf11.paragraphs[0].font.color.rgb = C_AMBER

p11_t = tf11.add_paragraph()
p11_t.text = "SolarSense: Production Impact & Deployed Architecture"
p11_t.font.size = Pt(24)
p11_t.font.bold = True
p11_t.font.color.rgb = C_TEXT_LIGHT

deploy_cards = [
    ("9-Stage Live Web Application", 
     "• End-to-end Flask web service with Jinja2 SSR and responsive amber design system.\n• Multi-Plant toggle (Plant 1 & Plant 2).\n• Complete 9 stages from upload intake, missing imputation lab, visual analytics, to inference.\n• Powered by Chart.js 4.4.3 visualizers."),
    ("Real-Time Explainable API", 
     "• RESTful endpoints: POST /api/predict & GET /api/bundle.\n• Zero-cost feature attributions using Ridge linear surrogate weights (+/- kW contributions).\n• Sub-second inference latency ready for energy management microservices."),
    ("Real-World CleanTech Value", 
     "• Enables community solar platforms (e.g. SundayGrids) to solve IoT dropouts and maintain auditable billing credit reconciliation.\n• Remote O&M soiling alerts save millions in physical site inspection costs.")
]

for i, (title, content) in enumerate(deploy_cards):
    left = Inches(1.0 + i * 3.85)
    card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(3.6), Inches(4.8))
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(30, 41, 59)
    card.line.color.rgb = RGBColor(51, 65, 85)
    card.line.width = Pt(1)

    tb = s11.shapes.add_textbox(left + Inches(0.2), Inches(2.0), Inches(3.2), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p.font.name = "Segoe UI"
    
    p2 = tf.add_paragraph()
    p2.text = content
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = RGBColor(226, 232, 240)
    p2.font.name = "Segoe UI"
    p2.space_before = Pt(8)

# Save Presentation
output_path = r"c:\Ml_Project\Solar_Sense\SolarSense_Project_Presentation.pptx"
prs.save(output_path)
print(f"Presentation saved successfully to: {output_path}")
