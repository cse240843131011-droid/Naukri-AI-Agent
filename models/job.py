from datetime import datetime
from models.user import db


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(150))
    salary = db.Column(db.String(100))
    match_score = db.Column(db.Integer)

    required_skills = db.Column(db.Text)
    missing_skills = db.Column(db.Text)
    reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JobApplication(db.Model):
    __tablename__ = "job_applications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    job_title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(150))
    salary = db.Column(db.String(100))

    status = db.Column(
        db.String(50),
        default="Applied"
    )

    applied_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Application {self.job_title}>"