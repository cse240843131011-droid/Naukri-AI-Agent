"""
services/resume_service.py
Business logic for resume upload, text extraction, and AI analysis.
"""
from __future__ import annotations
import json
import markdown
from datetime import datetime

from models.user import db
from models.resume import Resume

class ResumeService:
    """Handles resume CRUD + AI analysis orchestration."""

    def __init__(self, watsonx_service=None):
        self.wx = watsonx_service

    # ── Upload ────────────────────────────────────────────────────────────
    def save_resume(self, user_id: int, file_info: dict, raw_text: str = "") -> Resume:
        """
        Persist a newly uploaded resume to the database.
        file_info: dict returned by utils.save_upload()
        """
        # Un-set previous primary
        Resume.query.filter_by(user_id=user_id, is_primary=True).update({"is_primary": False})

        resume = Resume(
            user_id=user_id,
            filename=file_info["filename"],
            original_name=file_info["original_name"],
            file_path=file_info["file_path"],
            file_type=file_info["file_type"],
            raw_text=raw_text,
            is_primary=True,
            upload_date=datetime.utcnow(),
        )
        db.session.add(resume)
        db.session.commit()
        return resume

    # ── AI Analysis ───────────────────────────────────────────────────────
       # ── AI Analysis ───────────────────────────────────────────────────────
    def analyze(self, resume: Resume, user_profile: dict = None, job_description: str = None) -> dict:
        """
        Run Granite AI analysis on a resume.
        Returns analysis, HTML, ATS score and HTML report.
        """
        from prompts import resume_analysis_prompt, ats_scoring_prompt

        raw_text = resume.raw_text or ""
        if not raw_text:
            return {"error": "No text extracted from resume."}

        analysis_text = ""
        ats_result = ""

        if self.wx:
            analysis_text = self.wx.generate(
                resume_analysis_prompt(raw_text, user_profile)
            )

            ats_result = self.wx.generate(
                ats_scoring_prompt(raw_text, job_description)
            )

            print("=" * 80)
            print("ATS RESULT FROM GRANITE")
            print(ats_result)
            print("=" * 80)

        # Convert Markdown to HTML
        analysis_html = markdown.markdown(
            analysis_text,
            extensions=["tables", "fenced_code"]
        )

        ats_html = markdown.markdown(
            ats_result,
            extensions=["tables", "fenced_code"]
        )

        ats_score = self._parse_ats_score(
            ats_result or analysis_text
        )

        analysis_json = json.dumps({
            "analysis": analysis_text,
            "ats_analysis": ats_result,
        })

        resume.ats_score = ats_score
        resume.analysis_json = analysis_json
        resume.last_analyzed = datetime.utcnow()

        db.session.commit()

        return {
            "analysis_text": analysis_text,
            "analysis_html": analysis_html,
            "ats_result": ats_result,
            "ats_html": ats_html,
            "ats_score": ats_score,
        }
        ats_score = self._parse_ats_score(ats_result or analysis_text)

        analysis_json = json.dumps({
            "analysis": analysis_text,
            "ats_analysis": ats_result,
        })

        # Persist results
        resume.ats_score     = ats_score
        resume.analysis_json = analysis_json
        resume.last_analyzed = datetime.utcnow()
        db.session.commit()

        return {
            "analysis_text": analysis_text,
            "ats_result":    ats_result,
            "ats_score":     ats_score,
        }

    # ── Helpers ───────────────────────────────────────────────────────────
    @staticmethod
    def _parse_ats_score(text: str) -> float:
        """Try to pull an ATS score (0–100) from AI response text."""
        import re
        patterns = [
            r"ATS Score[:\s]+(\d+(?:\.\d+)?)",
            r"Score[:\s]+(\d+(?:\.\d+)?)/100",
            r"(\d{2,3}(?:\.\d+)?)\s*/\s*100",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                score = float(m.group(1))
                return min(100.0, max(0.0, score))
        return 0.0

    def get_resumes(self, user_id: int):
        return Resume.query.filter_by(user_id=user_id).order_by(Resume.upload_date.desc()).all()

    def get_primary(self, user_id: int) -> Resume | None:
        return Resume.query.filter_by(user_id=user_id, is_primary=True).first()

    def delete(self, resume: Resume) -> None:
        import os
        try:
            if resume.file_path and os.path.exists(resume.file_path):
                os.remove(resume.file_path)
        except OSError:
            pass
        db.session.delete(resume)
        db.session.commit()


