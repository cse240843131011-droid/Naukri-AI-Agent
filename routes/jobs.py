"""
routes/jobs.py
AI Job Recommendation & Application Routes
"""

from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    request,
)

from flask_login import login_required, current_user

from models.resume import Resume
from models.job import JobApplication
from models.user import db

from services.job_service import job_service

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


# ==========================================================
# AI JOB RECOMMENDATIONS
# ==========================================================

@jobs_bp.route("/")
@login_required
def index():

    resume = Resume.query.filter_by(
        user_id=current_user.id,
        is_primary=True
    ).first()

    if resume is None:
        flash("Please upload a resume first.", "warning")

        return render_template(
            "jobs/index.html",
            jobs=[],
            resume=None
        )

    result = job_service.recommend_jobs(resume)

    return render_template(
        "jobs/index.html",
        jobs=result.get("jobs", []),
        resume=resume
    )


# ==========================================================
# APPLY JOB
# ==========================================================

@jobs_bp.route("/apply", methods=["POST"])
@login_required
def apply():

    title = request.form.get("title")
    company = request.form.get("company")
    location = request.form.get("location")
    salary = request.form.get("salary")

    existing = JobApplication.query.filter_by(
        user_id=current_user.id,
        job_title=title,
        company=company
    ).first()

    if existing:
        flash("You have already applied for this job.", "warning")
        return redirect(url_for("jobs.index"))

    application = JobApplication(
        user_id=current_user.id,
        job_title=title,
        company=company,
        location=location,
        salary=salary,
        status="Applied"
    )

    db.session.add(application)
    db.session.commit()

    flash("Application submitted successfully!", "success")

    return redirect(url_for("jobs.index"))


# ==========================================================
# MY APPLICATIONS
# ==========================================================

@jobs_bp.route("/applications")
@login_required
def applications():

    applications = (
        JobApplication.query
        .filter_by(user_id=current_user.id)
        .order_by(JobApplication.applied_at.desc())
        .all()
    )

    return render_template(
        "jobs/applications.html",
        applications=applications
    )


# ==========================================================
# DELETE APPLICATION
# ==========================================================

@jobs_bp.route("/delete/<int:application_id>")
@login_required
def delete_application(application_id):

    application = JobApplication.query.filter_by(
        id=application_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(application)
    db.session.commit()

    flash("Application removed successfully.", "success")

    return redirect(url_for("jobs.applications"))