import os
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("LLM_API_KEY")

print("----------------------------------------")
print("✅ Environment Verification Successful!")
print(f"🔑 Loaded Key Placeholder: {api_key}")
print("----------------------------------------")