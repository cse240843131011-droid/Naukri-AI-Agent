"""
services/watsonx_service.py
IBM watsonx.ai Granite model service wrapper.
Falls back gracefully when API credentials are not configured.
"""
from __future__ import annotations
import traceback


class WatsonXService:
    """Wrapper around ibm-watsonx-ai ModelInference."""

    def __init__(self, app=None):
        self._client = None
        self._ready = False
        self._init_failed = False
        self._last_api_key = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app) -> None:
        api_key    = app.config.get("WATSONX_API_KEY", "")
        project_id = app.config.get("WATSONX_PROJECT_ID", "")

        # Only reset state when credentials actually change
        if api_key != self._last_api_key:
            self._last_api_key = api_key
            self._init_failed = False
            self._client = None

        self._api_key    = api_key
        self._project_id = project_id
        self._url = app.config.get(
            "WATSONX_URL",
            "https://us-south.ml.cloud.ibm.com"
        )
        self._model_id = app.config.get(
        "WATSONX_MODEL_ID",
        "ibm/granite-4-h-small"
        )

        self._max_tokens  = app.config.get("WATSONX_MAX_NEW_TOKENS", 1024)
        self._min_tokens  = app.config.get("WATSONX_MIN_NEW_TOKENS", 50)
        self._temperature = app.config.get("WATSONX_TEMPERATURE", 0.2)
        self._top_p       = app.config.get("WATSONX_TOP_P", 0.8)
        self._top_k       = app.config.get("WATSONX_TOP_K", 40)
        self._rep_penalty = app.config.get("WATSONX_REPETITION_PENALTY", 1.05)
        print("=" * 60)
        print("API KEY:", "Loaded" if self._api_key else "Missing")
        print("PROJECT ID:", "Loaded" if self._project_id else "Missing")
        print("MODEL:", self._model_id)
        print("=" * 60)
        self._ready = bool(self._api_key and self._project_id)
        print("=" * 60)
        print("READY :", self._ready)
        print("API KEY :", bool(self._api_key))
        print("PROJECT :", bool(self._project_id))
        print("MODEL :", self._model_id)
        print("=" * 60)

    def _get_model(self):

        if self._client:
            return self._client # Corrected indentation

        if not self._ready:
            print("WatsonX not ready.")
            return None

        if self._init_failed:
            print("WatsonX initialization previously failed.")
            return None
        try:

            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params

            creds = Credentials(
                api_key=self._api_key,
                url=self._url
            )

            params = {
                Params.MAX_NEW_TOKENS: self._max_tokens,
                Params.MIN_NEW_TOKENS: self._min_tokens,
                Params.TEMPERATURE: self._temperature,
                Params.TOP_P: self._top_p,
                Params.TOP_K: self._top_k,
                Params.REPETITION_PENALTY: self._rep_penalty,
            }

            self._client = ModelInference(
                model_id=self._model_id,
                credentials=creds,
                project_id=self._project_id,
                params=params,
            )

            return self._client

        except Exception as e: # Corrected indentation
            self._init_failed = True
            self._client = None

            print("=" * 60)
            print("IBM Initialization Error")
            print(type(e))
            print(e)
            traceback.print_exc()
            print("=" * 60)

            return None

    def generate(self, prompt: str) -> str:
        """
        Generate text using IBM watsonx.ai.
        """

        model = self._get_model()

        if model is None:
            return self._mock_response(prompt)

        try:
            response = model.generate_text(prompt=prompt)

            # Sometimes Granite returns reasoning before the final answer.
            # Remove common reasoning prefixes.
            bad_prefixes = [
                "The user says",
                "We need to",
                "Let's",
                "The prompt",
                "According to",
                "Reasoning",
            ]

            lines = response.splitlines()
            clean = []
            started = False

            for line in lines:
                text = line.strip()

                if not started:
                    if (
                        text == ""
                        or any(text.startswith(prefix) for prefix in bad_prefixes)
                    ):
                        continue

                    started = True

                clean.append(line)

            response = "\n".join(clean).strip()
            if response.startswith("```markdown"):
                response = response.replace("```markdown", "", 1)

            if response.startswith("```"):
                response = response.replace("```", "", 1)

            if response.endswith("```"):
                response = response[:-3]

            return response.strip()

        except Exception as e: # Corrected indentation
            print("=" * 70)
            print("IBM Generation Error")
            print(type(e))
            print(e)
            traceback.print_exc()
            print("=" * 70)

            return "[Error while generating AI response.]"
    def _mock_response(self, prompt: str) -> str:
        return (
            "🤖 **Naukri AI** is running in demo mode.\n\n"
            "To enable full AI-powered responses, please configure your "
            "`WATSONX_API_KEY` and `WATSONX_PROJECT_ID` in the `.env` file.\n\n"
            f"**Your prompt was received:** _{prompt[:120]}..._"
        )

    def is_ready(self) -> bool:
        return self._ready


watsonx = WatsonXService()