"""models/job.py — Job, SavedJob, JobApplication models"""
from datetime import datetime
from .user import db

class Job(db.Model):
    __tablename__ = "jobs"
    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(200), nullable=False)
    company       = db.Column(db.String(200), nullable=False)
    location      = db.Column(db.String(150))
    work_mode     = db.Column(db.String(30))
    job_type      = db.Column(db.String(30))      # fulltime|internship|parttime|contract
    experience_min= db.Column(db.Float, default=0)
    experience_max= db.Column(db.Float)
    salary_min    = db.Column(db.Float)
    salary_max    = db.Column(db.Float)
    skills_required = db.Column(db.Text)
    description   = db.Column(db.Text)
    apply_url     = db.Column(db.String(500))
    source        = db.Column(db.String(100))     # LinkedIn|Naukri|etc
    is_active     = db.Column(db.Boolean, default=True)
    posted_date   = db.Column(db.DateTime, default=datetime.utcnow)
    deadline      = db.Column(db.DateTime)

    def skills_list(self):
        return [s.strip() for s in (self.skills_required or "").split(",") if s.strip()]

class SavedJob(db.Model):
    __tablename__ = "saved_jobs"
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id   = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    job      = db.relationship("Job", backref="saves")

class JobApplication(db.Model):
    __tablename__ = "job_applications"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id      = db.Column(db.Integer, db.ForeignKey("jobs.id"))
    company     = db.Column(db.String(200))
    role        = db.Column(db.String(200))
    status      = db.Column(db.String(50), default="applied")
    # applied|screening|interview|offer|rejected|accepted|withdrawn
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    interview_date = db.Column(db.DateTime)
    notes       = db.Column(db.Text)
    job         = db.relationship("Job", backref="applications")
