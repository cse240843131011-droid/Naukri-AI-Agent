"""models/resume.py — Resume & ATS Score model"""
from datetime import datetime
from .user import db

class Resume(db.Model):
    __tablename__ = "resumes"
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename      = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    file_path     = db.Column(db.String(500))
    file_type     = db.Column(db.String(10))       # pdf | docx
    raw_text      = db.Column(db.Text)
    ats_score     = db.Column(db.Float, default=0)
    analysis_json = db.Column(db.Text)             # JSON blob from AI analysis
    is_primary    = db.Column(db.Boolean, default=False)
    upload_date   = db.Column(db.DateTime, default=datetime.utcnow)
    last_analyzed = db.Column(db.DateTime)

    def __repr__(self): return f"<Resume {self.original_name} score={self.ats_score}>"
