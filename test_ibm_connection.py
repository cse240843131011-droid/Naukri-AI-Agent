from dotenv import load_dotenv
import os
import traceback

load_dotenv()

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

try:
    creds = Credentials(
        api_key=os.getenv("WATSONX_API_KEY"),
        url=os.getenv("WATSONX_URL")
    )

    model = ModelInference(
        model_id=os.getenv("WATSONX_MODEL_ID"),
        credentials=creds,
        project_id=os.getenv("WATSONX_PROJECT_ID")
    )

    response = model.generate_text("Say hello in one sentence.")

    print("\nSUCCESS\n")
    print(response)

except Exception as e:
    print("\nERROR")
    print("=" * 60)
    print(type(e).__name__)
    print(e)
    traceback.print_exc()
    print("=" * 60)