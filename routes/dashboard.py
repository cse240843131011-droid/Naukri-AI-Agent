"""routes/dashboard.py — Dashboard blueprint"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from models.job import JobApplication, SavedJob
from models.resume import Resume

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/home")
@login_required
def home():
    resumes       = Resume.query.filter_by(user_id=current_user.id).count()
    applications  = JobApplication.query.filter_by(user_id=current_user.id).count()
    saved_jobs    = SavedJob.query.filter_by(user_id=current_user.id).count()
    recent_apps   = (JobApplication.query
                     .filter_by(user_id=current_user.id)
                     .order_by(JobApplication.applied_date.desc())
                     .limit(5).all())
    primary_resume = Resume.query.filter_by(user_id=current_user.id, is_primary=True).first()

    stats = {
        "resumes":      resumes,
        "applications": applications,
        "saved_jobs":   saved_jobs,
        "ats_score":    primary_resume.ats_score if primary_resume else 0,
    }
    return render_template("dashboard/home.html", stats=stats, recent_apps=recent_apps,
                           primary_resume=primary_resume)
