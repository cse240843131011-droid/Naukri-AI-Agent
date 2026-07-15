"""routes/resume.py — Resume upload, analysis, and management"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from models.user import db
from models.resume import Resume
from utils.file_handler import allowed_file, save_upload, extract_text
from services.resume_service import ResumeService
from services.watsonx_service import watsonx

resume_bp = Blueprint("resume", __name__)


def _get_service():
    svc = ResumeService(watsonx_service=watsonx)
    watsonx.init_app(current_app)
    return svc


@resume_bp.route("/")
@login_required
def index():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.upload_date.desc()).all()
    return render_template("resume/index.html", resumes=resumes)


@resume_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("resume")
        if not file or file.filename == "":
            flash("Please select a file.", "warning")
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash("Unsupported file type. Please upload PDF, DOCX, or TXT.", "danger")
            return redirect(request.url)

        file_info = save_upload(file, subfolder="resumes")
        raw_text  = extract_text(file_info["file_path"])

        svc    = _get_service()
        resume = svc.save_resume(current_user.id, file_info, raw_text)

        flash("Resume uploaded successfully!", "success")
        return redirect(url_for("resume.analyze", resume_id=resume.id))

    return render_template("resume/upload.html")


@resume_bp.route("/<int:resume_id>/analyze", methods=["GET", "POST"])
@login_required
def analyze(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    result = None

    if request.method == "POST":
        jd  = request.form.get("job_description", "").strip() or None
        svc = _get_service()
        result = svc.analyze(resume, current_user.to_profile_dict(), jd)

        db.session.refresh(resume)

        flash("Analysis complete!", "success")

    return render_template("resume/analyze.html", resume=resume, result=result)


@resume_bp.route("/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    svc = _get_service()
    svc.delete(resume)
    flash("Resume deleted.", "info")
    return redirect(url_for("resume.index"))


@resume_bp.route("/<int:resume_id>/set-primary", methods=["POST"])
@login_required
def set_primary(resume_id):
    Resume.query.filter_by(user_id=current_user.id, is_primary=True).update({"is_primary": False})
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    resume.is_primary = True
    db.session.commit()
    flash("Primary resume updated.", "success")
    return redirect(url_for("resume.index"))
