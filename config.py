import os
from dotenv import load_dotenv

# Load variables from .env when running locally.
# On deployment platforms, environment variables can be provided directly.
load_dotenv()


class Config:
    # ============================================================
    # Flask Security
    # ============================================================

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "smart-farming-development-secret-change-before-deployment"
    )

    # ============================================================
    # Database Configuration
    # ============================================================

    MYSQL_HOST = os.environ.get(
        "MYSQL_HOST",
        "localhost"
    )

    MYSQL_USER = os.environ.get(
        "MYSQL_USER",
        "root"
    )

    MYSQL_PASSWORD = os.environ.get(
        "MYSQL_PASSWORD",
        ""
    )

    MYSQL_DB = os.environ.get(
        "MYSQL_DB",
        "smart_farming_db"
    )

    MYSQL_PORT = int(
        os.environ.get(
            "MYSQL_PORT",
            "3306"
        )
    )

    # ============================================================
    # Machine Learning Model Paths
    # ============================================================

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    CROP_MODEL_PATH = os.path.join(
        BASE_DIR,
        "models",
        "crop_model.pkl"
    )

    DISEASE_MODEL_PATH = os.path.join(
        BASE_DIR,
        "models",
        "disease_model.pkl"
    )

    # ============================================================
    # Application Settings
    # ============================================================

    DEBUG = os.environ.get(
        "FLASK_DEBUG",
        "0"
    ).lower() in ("1", "true", "yes")

    HOST = os.environ.get(
        "HOST",
        "0.0.0.0"
    )

    PORT = int(
        os.environ.get(
            "PORT",
            "5000"
        )
    )

    # ============================================================
    # Supported Languages
    # ============================================================

    LANGUAGES = {
        "en": "English",
        "ta": "தமிழ் (Tamil)"
    }

    # ============================================================
    # Upload Settings
    # ============================================================

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB