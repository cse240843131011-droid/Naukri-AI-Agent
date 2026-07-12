"""routes/api.py — JSON REST API for external/AJAX consumers"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from services.watsonx_service import watsonx
from orchestrate.agent_coordinator import AgentCoordinator
from models.job import Job, JobApplication
from models.resume import Resume

api_bp = Blueprint("api", __name__)


def _coord():
    watsonx.init_app(current_app)
    return AgentCoordinator(watsonx=watsonx)


# ── Health ─────────────────────────────────────────────────────────────────
@api_bp.route("/health")
def health():
    watsonx.init_app(current_app)   # <-- Add this line

    return jsonify({
        "status": "ok",
        "watsonx_ready": watsonx.is_ready()
    })

# ── Agent chat (AJAX) ──────────────────────────────────────────────────────
@api_bp.route("/chat", methods=["POST"])
@login_required
def chat():
    data    = request.get_json(force=True) or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "message is required"}), 400

    coord  = _coord()
    result = coord.handle("chat", user_message=message,
                          conversation_history=history,
                          user_profile=current_user.to_profile_dict())
    return jsonify({"response": result})


# ── Resume ATS (AJAX) ──────────────────────────────────────────────────────
@api_bp.route("/ats-score", methods=["POST"])
@login_required
def ats_score():
    data          = request.get_json(force=True) or {}
    resume_text   = data.get("resume_text", "")
    job_description = data.get("job_description", "")

    if not resume_text:
        return jsonify({"error": "resume_text is required"}), 400

    coord  = _coord()
    result = coord.handle("ats_score", resume_text=resume_text,
                          job_description=job_description or None)
    return jsonify({"result": result})


# ── Jobs list (AJAX / mobile) ──────────────────────────────────────────────
@api_bp.route("/jobs")
@login_required
def jobs():
    jobs = Job.query.filter_by(is_active=True).order_by(Job.posted_date.desc()).limit(50).all()
    return jsonify([{
        "id": j.id, "title": j.title, "company": j.company,
        "location": j.location, "work_mode": j.work_mode,
        "job_type": j.job_type, "skills": j.skills_list(),
    } for j in jobs])


# ── User profile (AJAX) ────────────────────────────────────────────────────
@api_bp.route("/profile")
@login_required
def profile():
    return jsonify(current_user.to_profile_dict())
