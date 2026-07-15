from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("WATSONX_API_KEY")

print("Length:", len(key))
print("First 10:", key[:10])
print("Last 10 :", key[-10:])
print("Contains spaces:", " " in key)
print("Contains newline:", "\n" in key)