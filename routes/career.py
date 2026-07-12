"""routes/career.py — Career roadmap, skill gap, salary insights, cover letter"""
from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user

from services.watsonx_service import watsonx
from orchestrate.agent_coordinator import AgentCoordinator

career_bp = Blueprint("career", __name__)


def _coord():
    watsonx.init_app(current_app)
    return AgentCoordinator(watsonx=watsonx)


@career_bp.route("/")
@login_required
def index():
    return render_template("career/index.html")


@career_bp.route("/roadmap", methods=["GET", "POST"])
@login_required
def roadmap():
    result = None
    if request.method == "POST":
        current_role     = request.form.get("current_role", current_user.current_role or "").strip()
        target_role      = request.form.get("target_role",  current_user.target_role  or "").strip()
        experience_years = int(request.form.get("experience_years", current_user.experience_years or 0) or 0)
        education        = request.form.get("education", current_user.education or "").strip()
        coord  = _coord()
        result = coord.handle("career_roadmap", current_role=current_role,
                              target_role=target_role,
                              experience_years=experience_years,
                              education=education)
    return render_template("career/roadmap.html", result=result, user=current_user)


@career_bp.route("/skill-gap", methods=["GET", "POST"])
@login_required
def skill_gap():
    result = None
    if request.method == "POST":
        user_skills  = [s.strip() for s in request.form.get("user_skills", "").split(",") if s.strip()]
        target_role  = request.form.get("target_role", "").strip()
        jd           = request.form.get("job_description", "").strip() or None
        coord  = _coord()
        result = coord.handle("skill_gap", user_skills=user_skills,
                              target_role=target_role, job_description=jd)
    return render_template("career/skill_gap.html", result=result, user=current_user)


@career_bp.route("/salary", methods=["GET", "POST"])
@login_required
def salary():
    result = None
    if request.method == "POST":
        role             = request.form.get("role", "").strip()
        experience_years = int(request.form.get("experience_years", 0) or 0)
        location         = request.form.get("location", "India").strip()
        skills           = [s.strip() for s in request.form.get("skills", "").split(",") if s.strip()]
        coord  = _coord()
        result = coord.handle("salary_insight", role=role,
                              experience_years=experience_years,
                              location=location, skills=skills)
    return render_template("career/salary.html", result=result)


@career_bp.route("/cover-letter", methods=["GET", "POST"])
@login_required
def cover_letter():
    result = None
    if request.method == "POST":
        resume_text     = request.form.get("resume_text", "").strip()
        job_description = request.form.get("job_description", "").strip()
        company         = request.form.get("company", "").strip()
        role            = request.form.get("role", "").strip()
        coord  = _coord()
        result = coord.handle("cover_letter", resume_text=resume_text,
                              job_description=job_description,
                              company=company, role=role)
    return render_template("career/cover_letter.html", result=result)


@career_bp.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    result = None
    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        coord  = _coord()
        result = coord.handle("chat", user_message=user_message,
                              user_profile=current_user.to_profile_dict())
    return render_template("career/chat.html", result=result)
