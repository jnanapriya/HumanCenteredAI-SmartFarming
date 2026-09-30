import os
import joblib
import pandas as pd
import numpy as np

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from config import Config


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)
app.config.from_object(Config)


# ============================================================
# DEMO USER DATA
# ============================================================

DEFAULT_USER = {
    "id": 1,
    "name": "Ramesh Kumar",
    "email": "farmer@example.com",
    "phone": "+91 98765 43210",
    "location": "Coimbatore, Tamil Nadu",
    "preferred_language": "en"
}


DEFAULT_FARM = {
    "farm_name": "Green Valley Estate",
    "total_area": 5.5,
    "soil_type": "Loamy",
    "current_crop": "Rice (Paddy)",
    "previous_crop": "Pulses",
    "irrigation_type": "Canal & Borewell",
    "farming_experience": 12
}


# ============================================================
# MACHINE LEARNING MODEL MANAGEMENT
# ============================================================

OFFICIAL_FEATURE_ORDER = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
]

CROP_MODEL = None
CROP_MODEL_LOAD_ERROR = None


def load_crop_model():
    global CROP_MODEL
    global CROP_MODEL_LOAD_ERROR

    model_path = app.config.get("CROP_MODEL_PATH")

    if not model_path:
        CROP_MODEL_LOAD_ERROR = "Crop model path is not configured."
        print("[ML Engine Error] " + CROP_MODEL_LOAD_ERROR)
        return

    if not os.path.exists(model_path):
        CROP_MODEL = None
        CROP_MODEL_LOAD_ERROR = (
            f"Model file not found at '{model_path}'."
        )

        print(
            "[ML Engine Notice] "
            + CROP_MODEL_LOAD_ERROR
        )

        return

    try:
        CROP_MODEL = joblib.load(model_path)

        CROP_MODEL_LOAD_ERROR = None

        print(
            f"[ML Engine] Crop model loaded successfully "
            f"from '{model_path}'"
        )

    except Exception as e:
        CROP_MODEL = None

        CROP_MODEL_LOAD_ERROR = (
            f"Failed to load model file: {str(e)}"
        )

        print(
            "[ML Engine Error] "
            + CROP_MODEL_LOAD_ERROR
        )


# Load model when application starts
load_crop_model()


# ============================================================
# CROP PREDICTION
# ============================================================

def predict_crop_recommendation(
    n,
    p,
    k,
    temp,
    humidity,
    ph,
    rainfall
):
    """
    Run real ML inference using crop_model.pkl.

    Feature order:

    N
    P
    K
    temperature
    humidity
    ph
    rainfall
    """

    if CROP_MODEL is None:
        return {
            "error": True,
            "message": (
                "AI crop recommendation model is not loaded. "
                f"{CROP_MODEL_LOAD_ERROR}"
            )
        }

    try:

        # ----------------------------------------------------
        # Create model input
        # ----------------------------------------------------

        input_data = {
            "N": [float(n)],
            "P": [float(p)],
            "K": [float(k)],
            "temperature": [float(temp)],
            "humidity": [float(humidity)],
            "ph": [float(ph)],
            "rainfall": [float(rainfall)]
        }

        input_df = pd.DataFrame(
            input_data,
            columns=OFFICIAL_FEATURE_ORDER
        )

        # ----------------------------------------------------
        # Main prediction
        # ----------------------------------------------------

        predicted_raw = CROP_MODEL.predict(input_df)[0]

        predicted_crop = str(
            predicted_raw
        ).capitalize()

        # ----------------------------------------------------
        # Confidence / probabilities
        # ----------------------------------------------------

        confidence_pct = None
        confidence_level = "High"
        top_alternatives = []

        has_proba = hasattr(
            CROP_MODEL,
            "predict_proba"
        )

        top_prob = 0.0

        if has_proba:

            probas = CROP_MODEL.predict_proba(
                input_df
            )[0]

            classes = CROP_MODEL.classes_

            sorted_indices = np.argsort(
                probas
            )[::-1]

            top_index = sorted_indices[0]

            top_prob = float(
                probas[top_index]
            )

            confidence_pct = round(
                top_prob * 100,
                1
            )

            if confidence_pct >= 75:
                confidence_level = "High"

            elif confidence_pct >= 50:
                confidence_level = "Medium"

            else:
                confidence_level = "Low"

            # ------------------------------------------------
            # Top 3 alternatives
            # ------------------------------------------------

            for idx in sorted_indices[1:4]:

                alt_name = str(
                    classes[idx]
                ).capitalize()

                alt_probability = round(
                    float(probas[idx]) * 100,
                    1
                )

                top_alternatives.append(
                    {
                        "crop": alt_name,
                        "probability": alt_probability
                    }
                )

        # ----------------------------------------------------
        # Feature importance
        # ----------------------------------------------------

        feature_importances = {}

        if hasattr(
            CROP_MODEL,
            "feature_importances_"
        ):

            importances = (
                CROP_MODEL.feature_importances_
            )

            feature_names = getattr(
                CROP_MODEL,
                "feature_names_in_",
                OFFICIAL_FEATURE_ORDER
            )

            for feat_name, importance in zip(
                feature_names,
                importances
            ):

                score_pct = round(
                    float(importance) * 100,
                    1
                )

                if score_pct >= 20:
                    level = "High"

                elif score_pct >= 10:
                    level = "Moderate"

                else:
                    level = "Low"

                display_label = {
                    "N": "Nitrogen (N)",
                    "P": "Phosphorus (P)",
                    "K": "Potassium (K)",
                    "temperature": (
                        f"Temperature ({temp}°C)"
                    ),
                    "humidity": (
                        f"Humidity ({humidity}%)"
                    ),
                    "ph": (
                        f"Soil pH ({ph})"
                    ),
                    "rainfall": (
                        f"Rainfall ({rainfall}mm)"
                    )
                }.get(
                    feat_name,
                    feat_name
                )

                feature_importances[
                    display_label
                ] = {
                    "score": score_pct,
                    "level": level,
                    "raw_key": feat_name
                }

        # ----------------------------------------------------
        # Human-centered explanation
        # ----------------------------------------------------

        top_factors = sorted(
            feature_importances.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )[:2]

        if top_factors:

            top_factors_desc = ", ".join(
                [
                    name
                    for name, value in top_factors
                ]
            )

        else:

            top_factors_desc = (
                "soil and climate balance"
            )

        simple_explanation = (
            f"{predicted_crop} is strongly recommended "
            f"with "
            f"{confidence_pct if confidence_pct is not None else 'N/A'}%"
            f" model confidence. "
            f"The trained model evaluated key input "
            f"parameters, giving high weight to "
            f"{top_factors_desc} for optimal crop yield."
        )

        technical_explanation = (
            "Random Forest inference on Pandas "
            f"DataFrame vector "
            f"[N={n}, P={p}, K={k}, "
            f"temp={temp}, humidity={humidity}, "
            f"ph={ph}, rainfall={rainfall}]. "
            f"Primary predicted target: "
            f"'{predicted_raw}' "
            f"(max probability p={top_prob:.4f})."
        )

        # ----------------------------------------------------
        # Return prediction
        # ----------------------------------------------------

        return {
            "error": False,
            "crop": predicted_crop,
            "crop_raw": predicted_raw,
            "confidence": confidence_pct,
            "confidence_level": confidence_level,
            "has_proba": has_proba,
            "alternatives": top_alternatives,
            "feature_influences": feature_importances,
            "simple_explanation": simple_explanation,
            "technical_explanation": technical_explanation
        }

    except Exception as e:

        return {
            "error": True,
            "message": (
                "Inference execution failure: "
                f"{str(e)}"
            )
        }


# ============================================================
# GLOBAL TEMPLATE VARIABLES
# ============================================================

@app.context_processor
def inject_globals():

    return {
        "demo_mode": app.config.get(
            "DEMO_MODE",
            True
        ),

        "languages": app.config.get(
            "LANGUAGES",
            {
                "en": "English",
                "ta": "தமிழ் (Tamil)"
            }
        )
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    if "user_id" in session:
        return redirect(
            url_for("dashboard")
        )

    return redirect(
        url_for("login")
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # Demo login button
    if request.args.get("demo") == "1":

        session["user_id"] = DEFAULT_USER["id"]
        session["user_name"] = DEFAULT_USER["name"]
        session["user_email"] = DEFAULT_USER["email"]

        flash(
            "Logged in via Demo Mode.",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    # Normal demo login
    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # Demo behavior:
        # Any email/password is accepted.
        session["user_id"] = DEFAULT_USER["id"]

        if email and "@" in email:

            session["user_name"] = (
                email.split("@")[0]
                .replace(".", " ")
                .replace("_", " ")
                .title()
            )

        else:

            session["user_name"] = (
                DEFAULT_USER["name"]
            )

        session["user_email"] = (
            email
            if email
            else DEFAULT_USER["email"]
        )

        flash(
            "Login successful.",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html"
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        flash(
            "Registration completed in Demo Mode.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    model_configured = os.path.exists(
        app.config.get(
            "CROP_MODEL_PATH",
            ""
        )
    )

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        model_configured=model_configured
    )


# ============================================================
# PROFILE
# ============================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if request.method == "POST":

        flash(
            "Profile updated successfully in Demo Mode.",
            "success"
        )

    return render_template(
        "profile.html",
        active_page="profile",
        user=DEFAULT_USER,
        farm=DEFAULT_FARM
    )


# ============================================================
# SOIL ANALYSIS
# ============================================================

@app.route(
    "/soil-analysis",
    methods=["GET", "POST"]
)
def soil_analysis():

    return render_template(
        "soil_analysis.html",
        active_page="soil_analysis"
    )


# ============================================================
# CROP RECOMMENDATION
# ============================================================

@app.route(
    "/crop-recommendation",
    methods=["GET", "POST"]
)
def crop_recommendation():

    model_configured = (
        CROP_MODEL is not None
    )

    prediction = None
    input_data = None

    if request.method == "POST":

        try:

            raw_n = request.form.get(
                "nitrogen",
                ""
            ).strip()

            raw_p = request.form.get(
                "phosphorus",
                ""
            ).strip()

            raw_k = request.form.get(
                "potassium",
                ""
            ).strip()

            raw_temp = request.form.get(
                "temperature",
                ""
            ).strip()

            raw_humidity = request.form.get(
                "humidity",
                ""
            ).strip()

            raw_ph = request.form.get(
                "ph",
                ""
            ).strip()

            raw_rainfall = request.form.get(
                "rainfall",
                ""
            ).strip()

            # ------------------------------------------------
            # Required fields
            # ------------------------------------------------

            if not all(
                [
                    raw_n,
                    raw_p,
                    raw_k,
                    raw_temp,
                    raw_humidity,
                    raw_ph,
                    raw_rainfall
                ]
            ):

                flash(
                    "All soil and climate fields are required.",
                    "warning"
                )

            else:

                n = float(raw_n)
                p = float(raw_p)
                k = float(raw_k)
                temp = float(raw_temp)
                humidity = float(raw_humidity)
                ph = float(raw_ph)
                rainfall = float(raw_rainfall)

                input_data = {
                    "nitrogen": n,
                    "phosphorus": p,
                    "potassium": k,
                    "temperature": temp,
                    "humidity": humidity,
                    "ph": ph,
                    "rainfall": rainfall
                }

                # ------------------------------------------------
                # Validation
                # ------------------------------------------------

                if n < 0 or p < 0 or k < 0:

                    flash(
                        "N, P and K values cannot be negative.",
                        "danger"
                    )

                elif temp < -10 or temp > 60:

                    flash(
                        "Temperature must be between "
                        "-10°C and 60°C.",
                        "danger"
                    )

                elif humidity < 0 or humidity > 100:

                    flash(
                        "Humidity must be between "
                        "0% and 100%.",
                        "danger"
                    )

                elif ph < 0 or ph > 14:

                    flash(
                        "Soil pH must be between "
                        "0 and 14.",
                        "danger"
                    )

                elif rainfall < 0:

                    flash(
                        "Rainfall cannot be negative.",
                        "danger"
                    )

                else:

                    # ------------------------------------------------
                    # REAL ML PREDICTION
                    # ------------------------------------------------

                    result = predict_crop_recommendation(
                        n,
                        p,
                        k,
                        temp,
                        humidity,
                        ph,
                        rainfall
                    )

                    if result.get("error"):

                        flash(
                            result["message"],
                            "danger"
                        )

                    else:

                        prediction = result

                        confidence_text = (
                            f"{prediction['confidence']}%"
                            if prediction["confidence"]
                            is not None
                            else "N/A"
                        )

                        flash(
                            f"Model prediction generated: "
                            f"{prediction['crop']} "
                            f"({confidence_text} confidence)",
                            "success"
                        )

        except ValueError:

            flash(
                "Please enter valid numerical values.",
                "danger"
            )

        except Exception as e:

            flash(
                f"Unexpected error: {str(e)}",
                "danger"
            )

    return render_template(
        "crop_recommendation.html",
        active_page="crop_recommendation",
        prediction=prediction,
        input_data=input_data,
        model_configured=model_configured
    )


# ============================================================
# FERTILIZER
# ============================================================

@app.route(
    "/fertilizer",
    methods=["GET", "POST"]
)
def fertilizer():

    return render_template(
        "fertilizer.html",
        active_page="fertilizer"
    )


# ============================================================
# IRRIGATION
# ============================================================

@app.route(
    "/irrigation",
    methods=["GET", "POST"]
)
def irrigation():

    return render_template(
        "irrigation.html",
        active_page="irrigation"
    )


# ============================================================
# WEATHER
# ============================================================

@app.route("/weather")
def weather():

    return render_template(
        "weather.html",
        active_page="weather"
    )


# ============================================================
# DISEASE DETECTION
# ============================================================

@app.route(
    "/disease-detection",
    methods=["GET", "POST"]
)
def disease_detection():

    model_configured = os.path.exists(
        app.config.get(
            "DISEASE_MODEL_PATH",
            ""
        )
    )

    return render_template(
        "disease_detection.html",
        active_page="disease_detection",
        model_configured=model_configured
    )


# ============================================================
# DIGITAL TWIN
# ============================================================

@app.route("/digital-twin")
def digital_twin():

    return render_template(
        "digital_twin.html",
        active_page="digital_twin"
    )


# ============================================================
# WHAT-IF SIMULATION
# ============================================================

@app.route(
    "/simulation",
    methods=["GET", "POST"]
)
def simulation():

    return render_template(
        "simulation.html",
        active_page="simulation"
    )


# ============================================================
# YIELD PREDICTION
# ============================================================

@app.route(
    "/yield-prediction",
    methods=["GET", "POST"]
)
def yield_prediction():

    return render_template(
        "yield_prediction.html",
        active_page="yield_prediction"
    )


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():

    return render_template(
        "history.html",
        active_page="history"
    )


# ============================================================
# NOTIFICATIONS
# ============================================================

@app.route("/notifications")
def notifications():

    return render_template(
        "notifications.html",
        active_page="notifications"
    )


# ============================================================
# REPORTS
# ============================================================

@app.route("/reports")
def reports():

    return render_template(
        "reports.html",
        active_page="reports"
    )


# ============================================================
# FEEDBACK
# ============================================================

@app.route(
    "/feedback",
    methods=["POST"]
)
def feedback():

    usefulness = request.form.get(
        "usefulness"
    )

    comments = request.form.get(
        "comments"
    )

    flash(
        "Thank you for your feedback.",
        "success"
    )

    return redirect(
        url_for("crop_recommendation")
    )


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print("")
    print("=" * 60)
    print(" AgriSmart AI - Human-Centered AI Smart Farming")
    print("=" * 60)
    print("")
    print("Demo Mode: ON")
    print("URL: http://127.0.0.1:5000")
    print("Login: http://127.0.0.1:5000/login")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )