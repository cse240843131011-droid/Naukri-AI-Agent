"""
services/job_service.py
CRUD + matching logic for Job, SavedJob, and JobApplication models.
"""
from __future__ import annotations
from datetime import datetime

from models.user import db
from models.job import Job, SavedJob, JobApplication


class JobService:
    """Handles job search, save, and application tracking."""

    def __init__(self, watsonx_service=None):
        self.wx = watsonx_service

    # ── Jobs ──────────────────────────────────────────────────────────────
    def search(self, title: str = "", location: str = "", work_mode: str = "",
               job_type: str = "", experience_max: float = None):
        q = Job.query.filter_by(is_active=True)
        if title:
            q = q.filter(Job.title.ilike(f"%{title}%"))
        if location:
            q = q.filter(Job.location.ilike(f"%{location}%"))
        if work_mode:
            q = q.filter_by(work_mode=work_mode)
        if job_type:
            q = q.filter_by(job_type=job_type)
        if experience_max is not None:
            q = q.filter(Job.experience_min <= experience_max)
        return q.order_by(Job.posted_date.desc())

    def get_all_active(self):
        return Job.query.filter_by(is_active=True).order_by(Job.posted_date.desc()).all()

    def get_by_id(self, job_id: int) -> Job | None:
        return Job.query.get(job_id)

    def create(self, data: dict) -> Job:
        job = Job(**data)
        db.session.add(job)
        db.session.commit()
        return job

    # ── Saved Jobs ────────────────────────────────────────────────────────
    def save_job(self, user_id: int, job_id: int) -> SavedJob | None:
        existing = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
        if existing:
            return existing
        saved = SavedJob(user_id=user_id, job_id=job_id)
        db.session.add(saved)
        db.session.commit()
        return saved

    def unsave_job(self, user_id: int, job_id: int) -> bool:
        saved = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
        if saved:
            db.session.delete(saved)
            db.session.commit()
            return True
        return False

    def is_saved(self, user_id: int, job_id: int) -> bool:
        return SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first() is not None

    def get_saved_jobs(self, user_id: int):
        return (SavedJob.query
                .filter_by(user_id=user_id)
                .order_by(SavedJob.saved_at.desc())
                .all())

    # ── Applications ───────────────────────────────────────────────────────
    def apply(self, user_id: int, job_id: int = None, company: str = "",
              role: str = "", notes: str = "") -> JobApplication:
        app = JobApplication(
            user_id=user_id,
            job_id=job_id,
            company=company,
            role=role,
            notes=notes,
            applied_date=datetime.utcnow(),
        )
        db.session.add(app)
        db.session.commit()
        return app

    def update_status(self, application_id: int, status: str) -> bool:
        app = JobApplication.query.get(application_id)
        if app:
            app.status = status
            db.session.commit()
            return True
        return False

    def get_applications(self, user_id: int):
        return (JobApplication.query
                .filter_by(user_id=user_id)
                .order_by(JobApplication.applied_date.desc())
                .all())

    # ── AI Job Matching ────────────────────────────────────────────────────
    def ai_recommend(self, user_profile: dict, preferences: dict = None) -> str:
        """Return Granite AI job recommendations text."""
        if not self.wx:
            return "[WatsonX not configured]"
        from prompts import job_recommendation_prompt
        return self.wx.generate(job_recommendation_prompt(user_profile, preferences))
