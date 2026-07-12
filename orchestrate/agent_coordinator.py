"""
orchestrate/agent_coordinator.py
IBM Orchestrate-style agent coordinator.
Routes user intents to the correct Naukri AI agent/service.
"""
from __future__ import annotations
from services.watsonx_service import WatsonXService


INTENT_MAP = {
    "resume_analysis":    "resume",
    "ats_score":          "ats",
    "job_recommendation": "job",
    "skill_gap":          "resume",
    "career_roadmap":     "general",
    "interview_prep":     "interview",
    "coding_interview":   "coding",
    "company_research":   "general",
    "salary_insight":     "salary",
    "cover_letter":       "resume",
    "recruiter":          "recruiter",
    "chat":               "general",
}


class AgentCoordinator:
    """
    Central coordinator that routes requests to the appropriate
    prompt template and Granite model call.
    """

    def __init__(self, watsonx: WatsonXService = None):
        self.wx = watsonx

    # ------------------------------------------------------------------
    def handle(self, intent: str, **kwargs) -> str:
        """
        Dispatch an intent to the right prompt builder, call Granite,
        and return the response string.
        """
        handler = getattr(self, f"_handle_{intent}", self._handle_chat)
        return handler(**kwargs)

    # ── Intent handlers ────────────────────────────────────────────────
    def _handle_resume_analysis(self, resume_text: str = "", user_profile: dict = None, **_) -> str:
        from prompts import resume_analysis_prompt
        return self._generate(resume_analysis_prompt(resume_text, user_profile))

    def _handle_ats_score(self, resume_text: str = "", job_description: str = None, **_) -> str:
        from prompts import ats_scoring_prompt
        return self._generate(ats_scoring_prompt(resume_text, job_description))

    def _handle_job_recommendation(self, user_profile: dict = None, preferences: dict = None, **_) -> str:
        from prompts import job_recommendation_prompt
        return self._generate(job_recommendation_prompt(user_profile or {}, preferences))

    def _handle_skill_gap(self, user_skills: list = None, target_role: str = "", job_description: str = None, **_) -> str:
        from prompts import skill_gap_analysis_prompt
        return self._generate(skill_gap_analysis_prompt(user_skills or [], target_role, job_description))

    def _handle_career_roadmap(self, current_role: str = "", target_role: str = "",
                                experience_years: int = 0, education: str = "", **_) -> str:
        from prompts import career_roadmap_prompt
        return self._generate(career_roadmap_prompt(current_role, target_role, experience_years, education))

    def _handle_interview_prep(self, role: str = "", company: str = "",
                                experience_years: int = 0, interview_type: str = "full", **_) -> str:
        from prompts import interview_prep_prompt
        return self._generate(interview_prep_prompt(role, company, experience_years, interview_type))

    def _handle_coding_interview(self, topic: str = "Arrays", difficulty: str = "medium",
                                  language: str = "Python", num_questions: int = 3, **_) -> str:
        from prompts import coding_interview_prompt
        return self._generate(coding_interview_prompt(topic, difficulty, language, num_questions))

    def _handle_company_research(self, company: str = "", role: str = None, **_) -> str:
        from prompts import company_research_prompt
        return self._generate(company_research_prompt(company, role))

    def _handle_salary_insight(self, role: str = "", experience_years: int = 0,
                                location: str = "India", skills: list = None, **_) -> str:
        from prompts import salary_insight_prompt
        return self._generate(salary_insight_prompt(role, experience_years, location, skills))

    def _handle_cover_letter(self, resume_text: str = "", job_description: str = "",
                              company: str = "", role: str = "", **_) -> str:
        from prompts import cover_letter_prompt
        return self._generate(cover_letter_prompt(resume_text, job_description, company, role))

    def _handle_recruiter(self, job_description: str = "", candidate_resumes: list = None,
                           task: str = "rank", **_) -> str:
        from prompts import recruiter_assistant_prompt
        return self._generate(recruiter_assistant_prompt(job_description, candidate_resumes or [], task))

    def _handle_chat(self, user_message: str = "", conversation_history: list = None,
                     user_profile: dict = None, **_) -> str:
        from prompts import chat_assistant_prompt
        return self._generate(chat_assistant_prompt(user_message, conversation_history, user_profile))

    # ── Internal ───────────────────────────────────────────────────────
    def _generate(self, prompt: str) -> str:
        if self.wx:
            return self.wx.generate(prompt)
        return "[AgentCoordinator] WatsonX service not initialised."
