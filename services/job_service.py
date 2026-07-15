"""
services/job_service.py
AI-powered Job Recommendation Service using IBM Granite
"""

from __future__ import annotations

import json

from services.watsonx_service import watsonx


class JobService:
    """Generate AI job recommendations from resume content."""

    def __init__(self, watsonx_service=None):
        self.wx = watsonx_service or watsonx

    def recommend_jobs(self, resume):
        """
        Generate AI job recommendations from the user's resume.
        """

        resume_text = resume.raw_text or ""

        if not resume_text.strip():
            return {
                "success": False,
                "message": "Resume text is empty.",
                "jobs": []
            }

        ats_score = resume.ats_score or 0

        # -----------------------------
        # IMPROVED GRANITE PROMPT
        # -----------------------------
        prompt = f"""
You are an expert AI Career Advisor and Recruitment Consultant.

Your task is to analyze the candidate's resume and ATS score and recommend the TOP 5 most suitable jobs.

Candidate ATS Score:
{ats_score}

Resume:
{resume_text}

For each job recommendation provide:

- title
- company
- match (0-100)
- salary
- location
- required_skills
- missing_skills
- reason

Return ONLY valid JSON.

Example:

[
    {{
        "title": "Python Backend Developer",
        "company": "IBM",
        "match": 95,
        "salary": "₹8-12 LPA",
        "location": "Bangalore",
        "required_skills": [
            "Python",
            "Flask",
            "SQL"
        ],
        "missing_skills": [
            "Docker",
            "AWS"
        ],
        "reason": "Excellent Python and backend development profile."
    }}
]

Rules:

1. Return ONLY JSON.
2. Do NOT write markdown.
3. Do NOT write explanations.
4. Return exactly 5 jobs.
5. Match must be between 0 and 100.
6. Salary should be realistic for India.
"""

        try:

            response = self.wx.generate(prompt)
            print("=" * 80)
            print("RAW GRANITE RESPONSE")
            print(response)
            print("=" * 80)

            if not response:
                return {
                    "success": False,
                    "message": "Granite returned an empty response.",
                    "jobs": []
                }

            response = response.strip()

            # Remove markdown code fences
            if response.startswith("```json"):
                response = response.replace("```json", "", 1)

            if response.startswith("```"):
                response = response.replace("```", "", 1)

            if response.endswith("```"):
                response = response[:-3]

            response = response.strip()

            # -----------------------------
            # SAFE JSON PARSING
            # -----------------------------
            try:
                jobs = json.loads(response)

            except json.JSONDecodeError:

                start = response.find("[")

                end = response.rfind("]")

                if start != -1 and end != -1:
                    jobs = json.loads(response[start:end + 1])
                else:
                    raise

            return {
                "success": True,
                "jobs": jobs
            }

        except Exception as e:

            print("Job Recommendation Error:", e)

            return {
                "success": False,
                "message": str(e),
                "jobs": []
            }


job_service = JobService()