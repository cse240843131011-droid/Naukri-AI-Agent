"""routes/recruiter.py — Recruiter assistant: JD upload and candidate ranking"""
from flask import Blueprint, render_template, request, current_app, flash
from flask_login import login_required, current_user

from services.watsonx_service import watsonx
from orchestrate.agent_coordinator import AgentCoordinator
from utils.file_handler import extract_text

recruiter_bp = Blueprint("recruiter", __name__)


def _coord():
    watsonx.init_app(current_app)
    return AgentCoordinator(watsonx=watsonx)


@recruiter_bp.route("/")
@login_required
def index():
    return render_template("recruiter/index.html")


@recruiter_bp.route("/rank", methods=["GET", "POST"])
@login_required
def rank():
    result = None
    if request.method == "POST":
        jd_text          = request.form.get("job_description", "").strip()
        candidate_texts  = []

        # Accept pasted text blocks for each candidate (up to 5)
        for i in range(1, 6):
            ct = request.form.get(f"candidate_{i}", "").strip()
            if ct:
                candidate_texts.append(ct)

        # Also handle uploaded files
        for f in request.files.getlist("resume_files"):
            if f and f.filename:
                import tempfile, os
                suffix = "." + f.filename.rsplit(".", 1)[-1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    f.save(tmp.name)
                    text = extract_text(tmp.name)
                    if text:
                        candidate_texts.append(text)
                    os.unlink(tmp.name)

        if not jd_text:
            flash("Please provide a Job Description.", "warning")
        elif not candidate_texts:
            flash("Please provide at least one candidate resume.", "warning")
        else:
            coord  = _coord()
            result = coord.handle("recruiter", job_description=jd_text,
                                  candidate_resumes=candidate_texts, task="rank")

    return render_template("recruiter/rank.html", result=result)
