from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
import os

app = Flask(__name__)

# Store user states
user_sessions = {}

# Path to save Excel file
FILE_PATH = "users_data.xlsx"

# Ensure the file exists
if not os.path.exists(FILE_PATH):
    df = pd.DataFrame(columns=["Phone", "Name", "Email", "Query"])
    df.to_excel(FILE_PATH, index=False)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    global user_sessions

    # Get user phone number and message
    user_phone = request.values.get("From", "").split(":")[-1]
    incoming_msg = request.values.get("Body", "").strip()

    response = MessagingResponse()
    message = response.message()

    # Check user session
    if user_phone not in user_sessions:
        user_sessions[user_phone] = {"step": "ask_name"}
        message.body("Hello! What's your name?")
    elif user_sessions[user_phone]["step"] == "ask_name":
        user_sessions[user_phone]["name"] = incoming_msg
        user_sessions[user_phone]["step"] = "ask_email"
        message.body(f"Thanks, {incoming_msg}! What's your email?")
    elif user_sessions[user_phone]["step"] == "ask_email":
        user_sessions[user_phone]["email"] = incoming_msg
        user_sessions[user_phone]["step"] = "ask_query"
        message.body("Got it! What would you like to ask?")
    elif user_sessions[user_phone]["step"] == "ask_query":
        user_sessions[user_phone]["query"] = incoming_msg
        save_to_excel(user_phone, user_sessions[user_phone])
        del user_sessions[user_phone]  # Remove session after saving
        message.body("Thank you! Your details have been saved. We will get back to you soon.")

    return str(response)

def save_to_excel(phone, data):
    df = pd.read_excel(FILE_PATH)
    new_entry = pd.DataFrame([{
        "Phone": phone,
        "Name": data["name"],
        "Email": data["email"],
        "Query": data["query"]
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_excel(FILE_PATH, index=False)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
