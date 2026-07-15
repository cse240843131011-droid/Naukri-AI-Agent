from dotenv import load_dotenv
import os

load_dotenv()

print("API KEY :", os.getenv("WATSONX_API_KEY"))
print("PROJECT :", os.getenv("WATSONX_PROJECT_ID"))
print("URL     :", os.getenv("WATSONX_URL"))
print("MODEL   :", os.getenv("WATSONX_MODEL_ID"))