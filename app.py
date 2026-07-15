"""
app.py — IBM Naukri Agent: Flask Application Factory & Entry Point
"""
import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from config import get_config
from models.user import db, User


def create_app(config_class=None):
    """Application factory."""
    app = Flask(__name__)

    # ── Load Config ────────────────────────────────────────────────────────
    cfg = config_class or get_config()
    app.config.from_object(cfg)
    print("=" * 60)
    print("DATABASE URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    print("=" * 60)

    from services.watsonx_service import watsonx
    watsonx.init_app(app)

    # ── Ensure upload dirs exist ───────────────────────────────────────────
    for sub in ("resumes", "job_descriptions"):
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], sub), exist_ok=True)

    # ── Extensions ────────────────────────────────────────────────────────
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Register Blueprints ────────────────────────────────────────────────
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.resume import resume_bp
    from routes.jobs import jobs_bp
    from routes.interview import interview_bp
    from routes.recruiter import recruiter_bp
    from routes.career import career_bp
    from routes.api import api_bp
    from routes.about import about_bp

    app.register_blueprint(auth_bp,      url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(resume_bp,    url_prefix="/resume")
    app.register_blueprint(jobs_bp,      url_prefix="/jobs")
    app.register_blueprint(interview_bp, url_prefix="/interview")
    app.register_blueprint(recruiter_bp, url_prefix="/recruiter")
    app.register_blueprint(career_bp,    url_prefix="/career")
    app.register_blueprint(api_bp,       url_prefix="/api/v1")
    app.register_blueprint(about_bp,     url_prefix="/about")

    # ── Root redirect ──────────────────────────────────────────────────────
    from flask import redirect, url_for
    @app.route("/")
    def index():
        return redirect(url_for("dashboard.home"))

    # ── Error handlers ─────────────────────────────────────────────────────
    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        from flask import render_template
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # ── DB init ────────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app

import os
# ── Entry Point ────────────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5050)),
        debug=app.config.get("DEBUG", True),
    )
