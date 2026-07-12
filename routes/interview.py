"""routes/interview.py — Interview preparation and coding challenge routes"""
from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user

from services.watsonx_service import watsonx
from orchestrate.agent_coordinator import AgentCoordinator

interview_bp = Blueprint("interview", __name__)


def _coord():
    watsonx.init_app(current_app)
    return AgentCoordinator(watsonx=watsonx)


@interview_bp.route("/")
@login_required
def index():
    return render_template("interview/index.html")


@interview_bp.route("/prep", methods=["GET", "POST"])
@login_required
def prep():
    result = None
    if request.method == "POST":
        role             = request.form.get("role", "").strip()
        company          = request.form.get("company", "").strip()
        experience_years = int(request.form.get("experience_years", 0) or 0)
        interview_type   = request.form.get("interview_type", "full")
        coord  = _coord()
        result = coord.handle("interview_prep",
                              role=role, company=company,
                              experience_years=experience_years,
                              interview_type=interview_type)
    return render_template("interview/prep.html", result=result)


@interview_bp.route("/coding", methods=["GET", "POST"])
@login_required
def coding():
    result = None
    if request.method == "POST":
        topic        = request.form.get("topic", "Arrays")
        difficulty   = request.form.get("difficulty", "medium")
        language     = request.form.get("language", "Python")
        num_questions= int(request.form.get("num_questions", 3) or 3)
        coord  = _coord()
        result = coord.handle("coding_interview",
                              topic=topic, difficulty=difficulty,
                              language=language, num_questions=num_questions)
    return render_template("interview/coding.html", result=result)


@interview_bp.route("/company-research", methods=["GET", "POST"])
@login_required
def company_research():
    result = None
    if request.method == "POST":
        company = request.form.get("company", "").strip()
        role    = request.form.get("role", "").strip() or None
        coord   = _coord()
        result  = coord.handle("company_research", company=company, role=role)
    return render_template("interview/company_research.html", result=result)
