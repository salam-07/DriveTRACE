from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API")

# --- Gemini 2.5 API Feedback System ---
import requests

LOGS_PATH = os.path.join(os.path.dirname(__file__), 'Logs', 'driving_warnings.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'Logs', 'ai_feedback.txt')

def load_driving_warnings():
    """Load driving warnings from the CSV file as a string."""
    try:
        with open(LOGS_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Could not load driving warnings: {e}"

def get_gemini_feedback(warnings, api_key):
    """Send driving warnings to Gemini 2.5 and get detailed instructor feedback."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + api_key
    headers = {"Content-Type": "application/json"}
    prompt = (
        "You are a professional driving instructor. "
        "Given the following driving warnings (from a driving simulation), provide concise, actionable feedback for the driver. "
        "Point out specific bad habits but dont repeat the warnings' text, explain why they are dangerous, and give actionable advice on how to improve. "
        "Format your text clearly. No markdown or special formatting needed, just plain text. Have line breaks and numbered lists for clarity. No use of asteriks"
        "Format your response as such: 1. [Problem Detected] (describe issue). Tell Number of occurences. Inform the danger. Inform actionable insights. Use same format for all types of problems."
        "Be constructive, thorough, and use clear language. If a specific warning is shown less times, or more times, acknowledge that as well.\n\n"
        f"Driving Warnings (CSV):\n{warnings}\n\nFeedback:"
    )
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        # Gemini API returns the text in a nested structure
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error getting feedback: {e}"

def save_feedback(feedback):
    """Save feedback to a txt file, overwriting previous content."""
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(feedback)

def generate_and_save_feedback():
    warnings = load_driving_warnings()
    feedback = get_gemini_feedback(warnings, API_KEY)
    save_feedback(feedback)
    print("Feedback generated and saved to ai_feedback.txt.")


