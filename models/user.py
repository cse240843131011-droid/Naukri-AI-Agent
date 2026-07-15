"""models/user.py — User model with roles"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(30), default="student")   # student|fresher|experienced|recruiter|admin
    phone         = db.Column(db.String(20))
    location      = db.Column(db.String(100))
    current_role  = db.Column(db.String(100))
    target_role   = db.Column(db.String(100))
    experience_years = db.Column(db.Float, default=0)
    education     = db.Column(db.String(200))
    skills        = db.Column(db.Text)             # comma-separated
    certifications= db.Column(db.Text)
    linkedin_url  = db.Column(db.String(200))
    github_url    = db.Column(db.String(200))
    preferred_companies = db.Column(db.Text)
    preferred_location  = db.Column(db.String(100))
    expected_salary     = db.Column(db.String(50))
    work_mode     = db.Column(db.String(30), default="any")       # remote|hybrid|onsite|any
    avatar        = db.Column(db.String(200), default="default.png")
    dark_mode     = db.Column(db.Boolean, default=False)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime)

    resumes       = db.relationship("Resume", backref="owner", lazy=True)
    applications  = db.relationship("JobApplication", backref="applicant", lazy=True)
    
    def set_password(self, pw):  self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

    def skills_list(self):
        return [s.strip() for s in (self.skills or "").split(",") if s.strip()]

    def certifications_list(self):
        return [s.strip() for s in (self.certifications or "").split(",") if s.strip()]

    def to_profile_dict(self):
        return {
            "name": self.name, "email": self.email, "role": self.role,
            "location": self.location, "current_role": self.current_role,
            "target_role": self.target_role, "experience_years": self.experience_years,
            "education": self.education, "skills": self.skills_list(),
            "certifications": self.certifications_list(), "linkedin_url": self.linkedin_url,
            "github_url": self.github_url, "expected_salary": self.expected_salary,
            "work_mode": self.work_mode,
        }

    def __repr__(self): return f"<User {self.email}>"
