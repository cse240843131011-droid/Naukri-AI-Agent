"""
config.py — Centralised configuration for IBM Naukri Agent
All sensitive credentials are loaded from environment variables / .env
"""
import os
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()


class Config:
    # ── Flask ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    TESTING = False

    # ── File Uploads ───────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = set(
        os.environ.get("ALLOWED_EXTENSIONS", "pdf,docx,doc,txt").split(",")
    )

    # ── Database ───────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///naukri_agent.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── IBM watsonx.ai ─────────────────────────────────────────────────────
    WATSONX_API_KEY = os.environ.get("WATSONX_API_KEY", "")
    WATSONX_PROJECT_ID = os.environ.get("WATSONX_PROJECT_ID", "")
    WATSONX_URL = os.environ.get(
        "WATSONX_URL", "https://us-south.ml.cloud.ibm.com"
    )

    # UPDATED MODEL (Supported by your IBM environment)
    WATSONX_MODEL_ID = os.environ.get(
    "WATSONX_MODEL_ID",
    "ibm/granite-4-h-small"
    )

    # Generation Parameters
    WATSONX_MAX_NEW_TOKENS = 2048
    WATSONX_MIN_NEW_TOKENS = 50
    WATSONX_TEMPERATURE = 0.7
    WATSONX_TOP_P = 0.95
    WATSONX_TOP_K = 50
    WATSONX_REPETITION_PENALTY = 1.1

    # ── IBM Orchestrate ────────────────────────────────────────────────────
    IBM_ORCHESTRATE_API_KEY = os.environ.get("IBM_ORCHESTRATE_API_KEY", "")
    IBM_ORCHESTRATE_URL = os.environ.get(
        "IBM_ORCHESTRATE_URL",
        "https://api.us-south.orchestrate.cloud.ibm.com/v1",
    )
    IBM_ORCHESTRATE_INSTANCE_ID = os.environ.get(
        "IBM_ORCHESTRATE_INSTANCE_ID", ""
    )

    # ── IBM Watson Discovery (RAG) ─────────────────────────────────────────
    WATSON_DISCOVERY_API_KEY = os.environ.get(
        "WATSON_DISCOVERY_API_KEY", ""
    )
    WATSON_DISCOVERY_URL = os.environ.get("WATSON_DISCOVERY_URL", "")
    WATSON_DISCOVERY_ENV_ID = os.environ.get(
        "WATSON_DISCOVERY_ENV_ID", ""
    )
    WATSON_DISCOVERY_COLLECTION_ID = os.environ.get(
        "WATSON_DISCOVERY_COLLECTION_ID", ""
    )

    # ── IBM Cloud Object Storage ───────────────────────────────────────────
    IBM_COS_API_KEY = os.environ.get("IBM_COS_API_KEY", "")
    IBM_COS_INSTANCE_ID = os.environ.get("IBM_COS_INSTANCE_ID", "")
    IBM_COS_ENDPOINT = os.environ.get("IBM_COS_ENDPOINT", "")
    IBM_COS_BUCKET = os.environ.get(
        "IBM_COS_BUCKET", "naukri-agent-uploads"
    )

    # ── Redis ──────────────────────────────────────────────────────────────
    REDIS_URL = os.environ.get(
        "REDIS_URL", "redis://localhost:6379/0"
    )

    # ── Email ──────────────────────────────────────────────────────────────
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = (
        os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
    )
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")

    # ── Admin ──────────────────────────────────────────────────────────────
    ADMIN_EMAIL = os.environ.get(
        "ADMIN_EMAIL", "admin@naukriagent.com"
    )
    ADMIN_PASSWORD = os.environ.get(
        "ADMIN_PASSWORD", "Admin@123456"
    )


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///naukri_dev.db"
    )


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///naukri_prod.db"
    )

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return config_map.get(env, DevelopmentConfig)