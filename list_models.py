import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Retrieve Groq API Key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("Error: GROQ_API_KEY is missing from .env file!")
    exit()

# Initialize Groq client
client = Groq(api_key=api_key)

print("🔍 Fetching available models from Groq...\n")

try:
    # Get the list of models from Groq API
    models = client.models.list()
    
    print("✅ Available Models:")
    print("-" * 40)
    for model in models.data:
        print(f"- {model.id}")
    print("-" * 40)
    
except Exception as e:
    print(f"❌ Error fetching models: {e}")