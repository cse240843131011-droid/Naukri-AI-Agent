"""
routes/dashboard.py
Dashboard blueprint
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.resume import Resume
from models.job import JobApplication

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/home")
@login_required
def home():

    # Dashboard Statistics
    resumes = Resume.query.filter_by(
        user_id=current_user.id
    ).count()

    applications = JobApplication.query.filter_by(
        user_id=current_user.id
    ).count()

    primary_resume = Resume.query.filter_by(
        user_id=current_user.id,
        is_primary=True
    ).first()

    ats_score = (
        primary_resume.ats_score
        if primary_resume and primary_resume.ats_score
        else 0
    )

    recent_apps = (
        JobApplication.query
        .filter_by(user_id=current_user.id)
        .order_by(JobApplication.applied_at.desc())
        .limit(5)
        .all()
    )

    stats = {
        "resumes": resumes,
        "applications": applications,
        "ats_score": ats_score,
        "recommended_jobs": 5,
    }

    return render_template(
        "dashboard/home.html",
        stats=stats,
        recent_apps=recent_apps,
        primary_resume=primary_resume,
    )