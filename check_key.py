from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("WATSONX_API_KEY")

print("Length:", len(key))
print("Starts with:", key[:10])