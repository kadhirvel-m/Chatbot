import os
from flask import Flask, render_template, request, session, redirect, url_for
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "4f3c"

# Fetch OpenRouter API Key from .env file
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initial relaxation and support messages
initial_messages = [
    "Hello, I'm your mental health support chatbot. How can I help you today?",
    "If you're feeling stressed, try taking a deep breath. I'm here to listen.",
    "Remember, self-care is important. Let’s talk about how you're feeling."
]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["user_data"] = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "gender": request.form.get("gender"),
            "mood": request.form.get("mood"),
            "stress_level": request.form.get("stress_level"),
            "sleep_hours": request.form.get("sleep_hours"),
            "exercise": request.form.get("exercise"),
            "daily_routine": request.form.get("daily_routine"),
            "hobbies": request.form.get("hobbies"),
        }
        return redirect(url_for("chat"))  # Redirect to chat page

    return render_template("index.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_data" not in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        user_input = request.form["message"]
        session.setdefault("chat_history", []).append({"user": user_input})

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "mistralai/mistral-saba",  
            "messages": [
                {"role": "system", "content": f"You are a mental health chatbot providing support to {session['user_data']['name']}."},
                {"role": "user", "content": user_input}
            ]
        }

        response = requests.post(OPENROUTER_BASE_URL, headers=headers, data=json.dumps(payload))

        # DEBUG: Print API response
        print("STATUS CODE:", response.status_code)
        print("RESPONSE TEXT:", response.text)

        if response.status_code == 200:
            response_json = response.json()
            if "choices" in response_json and response_json["choices"]:
                bot_reply = response_json["choices"][0]["message"]["content"]
                
                # Convert numbered points to HTML bullet points
                bot_reply = bot_reply.replace("1.", "<br>🔹").replace("2.", "<br>🔹")\
                                    .replace("3.", "<br>🔹").replace("4.", "<br>🔹")\
                                    .replace("5.", "<br>🔹").replace("6.", "<br>🔹")\
                                    .replace("7.", "<br>🔹").replace("8.", "<br>🔹")\
                                    .replace("9.", "<br>🔹").replace("10.", "<br>🔹")
            else:
                bot_reply = "Sorry, I couldn't understand that."
        else:
            bot_reply = "Sorry, I couldn't process your request right now."

        session["chat_history"].append({"bot": bot_reply})
    else:
        session["chat_history"] = [{"bot": msg} for msg in initial_messages]

    return render_template("chat.html", chat_history=session["chat_history"], user_data=session["user_data"])

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render’s PORT env variable or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)

