"""routes/jobs.py — Job listing, search, save, and application tracking"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user

from models.job import Job, JobApplication
from services.job_service import JobService
from services.watsonx_service import watsonx
from utils.helpers import paginate_query

jobs_bp = Blueprint("jobs", __name__)


def _svc():
    watsonx.init_app(current_app)
    return JobService(watsonx_service=watsonx)


@jobs_bp.route("/")
@login_required
def index():
    svc   = _svc()
    title = request.args.get("title", "")
    loc   = request.args.get("location", "")
    mode  = request.args.get("work_mode", "")
    jtype = request.args.get("job_type", "")
    page  = int(request.args.get("page", 1))

    q    = svc.search(title=title, location=loc, work_mode=mode, job_type=jtype)
    jobs = paginate_query(q, page, per_page=12)
    return render_template("jobs/index.html", jobs=jobs, title=title,
                           location=loc, work_mode=mode, job_type=jtype)


@jobs_bp.route("/<int:job_id>")
@login_required
def detail(job_id):
    svc = _svc()
    job = svc.get_by_id(job_id) or __import__("flask").abort(404)
    is_saved = svc.is_saved(current_user.id, job_id)
    already_applied = JobApplication.query.filter_by(
        user_id=current_user.id, job_id=job_id).first() is not None
    return render_template("jobs/detail.html", job=job,
                           is_saved=is_saved, already_applied=already_applied)


@jobs_bp.route("/<int:job_id>/save", methods=["POST"])
@login_required
def save(job_id):
    svc = _svc()
    svc.save_job(current_user.id, job_id)
    flash("Job saved!", "success")
    return redirect(url_for("jobs.detail", job_id=job_id))


@jobs_bp.route("/<int:job_id>/unsave", methods=["POST"])
@login_required
def unsave(job_id):
    svc = _svc()
    svc.unsave_job(current_user.id, job_id)
    flash("Job removed from saved list.", "info")
    return redirect(url_for("jobs.saved"))


@jobs_bp.route("/saved")
@login_required
def saved():
    svc   = _svc()
    items = svc.get_saved_jobs(current_user.id)
    return render_template("jobs/saved.html", saved_jobs=items)


@jobs_bp.route("/<int:job_id>/apply", methods=["POST"])
@login_required
def apply(job_id):
    svc = _svc()
    job = svc.get_by_id(job_id)
    svc.apply(current_user.id, job_id=job_id,
               company=job.company if job else "",
               role=job.title if job else "")
    flash("Application tracked!", "success")
    return redirect(url_for("jobs.applications"))


@jobs_bp.route("/applications")
@login_required
def applications():
    svc  = _svc()
    apps = svc.get_applications(current_user.id)
    return render_template("jobs/applications.html", applications=apps)


@jobs_bp.route("/applications/<int:app_id>/status", methods=["POST"])
@login_required
def update_status(app_id):
    svc    = _svc()
    status = request.form.get("status", "applied")
    svc.update_status(app_id, status)
    flash("Application status updated.", "success")
    return redirect(url_for("jobs.applications"))


@jobs_bp.route("/ai-recommend")
@login_required
def ai_recommend():
    svc    = _svc()
    result = svc.ai_recommend(current_user.to_profile_dict())
    return render_template("jobs/ai_recommend.html", result=result)
