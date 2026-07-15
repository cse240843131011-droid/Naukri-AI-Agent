
"""
routes/career.py
Career Tools Routes
"""

from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user

import markdown

from services.watsonx_service import watsonx
from orchestrate.agent_coordinator import AgentCoordinator


career_bp = Blueprint(
    "career",
    __name__
)


# =====================================================
# Granite Coordinator
# =====================================================

def _coord():

    watsonx.init_app(current_app)

    return AgentCoordinator(
        watsonx=watsonx
    )


# =====================================================
# Career Home
# =====================================================

@career_bp.route("/")
@login_required
def index():

    return render_template(
        "career/index.html"
    )


# =====================================================
# Career Roadmap
# =====================================================

@career_bp.route(
    "/roadmap",
    methods=["GET", "POST"]
)
@login_required
def roadmap():

    result = None
    result_html = None

    if request.method == "POST":

        current_role = request.form.get(
            "current_role",
            current_user.current_role or ""
        ).strip()

        target_role = request.form.get(
            "target_role",
            current_user.target_role or ""
        ).strip()

        experience_years = int(

            request.form.get(
                "experience_years",
                current_user.experience_years or 0
            ) or 0

        )

        education = request.form.get(
            "education",
            current_user.education or ""
        ).strip()

        coord = _coord()
        result = coord.handle(

            "career_roadmap",

            current_role=current_role,

            target_role=target_role,

            experience_years=experience_years,

            education=education

        )

        if result:

            result_html = markdown.markdown(

                result,

                extensions=[
                    "tables",
                    "fenced_code",
                    "nl2br"
                ]

            )

    return render_template(

        "career/roadmap.html",

        result=result,

        result_html=result_html,

        user=current_user

    )


# =====================================================
# Skill Gap Analysis
# =====================================================

@career_bp.route(
    "/skill-gap",
    methods=["GET", "POST"]
)
@login_required
def skill_gap():

    result = None
    result_html = None

    if request.method == "POST":

        user_skills = [

            skill.strip()

            for skill in request.form.get(
                "user_skills",
                ""
            ).split(",")

            if skill.strip()

        ]

        target_role = request.form.get(
            "target_role",
            ""
        ).strip()

        job_description = request.form.get(
            "job_description",
            ""
        ).strip()

        coord = _coord()
        result = coord.handle(

            "skill_gap",

            user_skills=user_skills,

            target_role=target_role,

            job_description=job_description

        )

        if result:

            result_html = markdown.markdown(

                result,

                extensions=[
                    "tables",
                    "fenced_code",
                    "nl2br"
                ]

            )

    return render_template(

        "career/skill_gap.html",

        result=result,

        result_html=result_html,

        user=current_user

    )


# =====================================================
# Salary Insight
# =====================================================

@career_bp.route(
    "/salary",
    methods=["GET", "POST"]
)
@login_required
def salary():

    result = None
    result_html = None

    if request.method == "POST":

        role = request.form.get(
            "role",
            ""
        ).strip()

        experience_years = int(

            request.form.get(
                "experience_years",
                0
            ) or 0

        )

        location = request.form.get(
            "location",
            "India"
        ).strip()

        skills = [

            skill.strip()

            for skill in request.form.get(
                "skills",
                ""
            ).split(",")

            if skill.strip()

        ]

        coord = _coord()

        result = coord.handle(

            "salary_insight",

            role=role,

            experience_years=experience_years,

            location=location,

            skills=skills

        )

        if result:

            result_html = markdown.markdown(

                result,

                extensions=[
                    "tables",
                    "fenced_code",
                    "nl2br"
                ]

            )

    return render_template(

        "career/salary.html",

        result=result,

        result_html=result_html

    )
    # =====================================================
# Cover Letter Generator
# =====================================================

@career_bp.route(
    "/cover-letter",
    methods=["GET", "POST"]
)
@login_required
def cover_letter():

    result = None
    result_html = None

    if request.method == "POST":

        resume_text = request.form.get(
            "resume_text",
            ""
        ).strip()

        job_description = request.form.get(
            "job_description",
            ""
        ).strip()

        company = request.form.get(
            "company",
            ""
        ).strip()

        role = request.form.get(
            "role",
            ""
        ).strip()

        coord = _coord()

        result = coord.handle(

            "cover_letter",

            resume_text=resume_text,

            job_description=job_description,

            company=company,

            role=role

        )

        if result:

            result_html = markdown.markdown(

                result,

                extensions=[
                    "tables",
                    "fenced_code",
                    "nl2br"
                ]

            )

    return render_template(

        "career/cover_letter.html",

        result=result,

        result_html=result_html

    )


# =====================================================
# AI Career Chat
# =====================================================

@career_bp.route(
    "/chat",
    methods=["GET", "POST"]
)
@login_required
def chat():

    result = None
    result_html = None

    if request.method == "POST":

        user_message = request.form.get(
            "message",
            ""
        ).strip()

        coord = _coord()

        result = coord.handle(

            "chat",

            user_message=user_message,

            user_profile=current_user.to_profile_dict()

        )

        if result:

            result_html = markdown.markdown(

                result,

                extensions=[
                    "tables",
                    "fenced_code",
                    "nl2br"
                ]

            )

    return render_template(

        "career/chat.html",

        result=result,

        result_html=result_html

    )