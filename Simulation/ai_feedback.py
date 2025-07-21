from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API")

print(f"Your API Key is: {API_KEY}")