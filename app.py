import streamlit as st
import requests
import json
import matplotlib.pyplot as plt
import datetime
import os

# -------------------------------
# Configuration
# -------------------------------
API_KEY = "AIzaSyDTfeVdMUysaNLYGxThI66euHeZOmz3f_4"  
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
LOG_FILE = "blood_sugar_log.json"

# -------------------------------
# Utility Functions
# -------------------------------
def get_latest_sugar_info():
    entries = load_blood_sugar_history()
    if not entries:
        return None, None

    levels = [e["level"] for e in entries]
    latest = levels[-1]

    if len(levels) >= 3:
        trend = "rising" if levels[-1] > levels[-2] > levels[-3] else \
                "falling" if levels[-1] < levels[-2] < levels[-3] else "stable"
    else:
        trend = "stable"

    return latest, trend


def get_gemini_response(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        return response_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("Gemini API error:", e)
        return "⚠️ Sorry, I couldn't process your request."


def get_context_aware_response(user_input):
    latest_level, trend = get_latest_sugar_info()

    if latest_level is not None and "diet" in user_input.lower():
        context = f"My latest blood sugar reading is {latest_level} mg/dL and the trend is {trend}. "
        prompt = context + "Based on this, " + user_input
    else:
        prompt = user_input

    return get_gemini_response(prompt)


def save_blood_sugar_entry(level):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "level": level
    }
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_blood_sugar_history():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return json.load(f)


def plot_blood_sugar_graph(entries):
    if not entries:
        st.info("No blood sugar data available yet.")
        return

    dates = [datetime.datetime.fromisoformat(e["timestamp"]) for e in entries]
    levels = [e["level"] for e in entries]

    plt.figure(figsize=(10, 4))
    plt.plot(dates, levels, marker='o', linestyle='-')
    plt.xlabel("Date")
    plt.ylabel("Blood Sugar Level (mg/dL)")
    plt.title("Blood Sugar Trend Over Time")
    plt.grid(True)
    st.pyplot(plt)

# -------------------------------
# Streamlit App Interface
# -------------------------------
st.set_page_config(page_title="Diabetes Management Assistant", page_icon="💬")
st.title("💬 Diabetes Management Assistant")

menu = st.sidebar.radio("Select Function", [
    "💬 Chatbot",
    "📈 Log Blood Sugar",
    "📊 View Blood Sugar Graph",
    "💡 Health Tips"
])

# -------------------------------
# Chatbot
# -------------------------------
if menu == "💬 Chatbot":
    st.subheader("Ask Anything About Diabetes")
    user_input = st.text_input("Ask a question:")
    if st.button("Ask") and user_input:
        response = get_context_aware_response(user_input)
        st.markdown(response)

# -------------------------------
# Blood Sugar Logging
# -------------------------------
elif menu == "📈 Log Blood Sugar":
    st.subheader("📥 Enter Blood Sugar Level")
    level = st.number_input("Blood Sugar Level (mg/dL)", min_value=40, max_value=500, step=1)
    if st.button("Save Entry"):
        save_blood_sugar_entry(level)
        st.success("Blood sugar level saved successfully!")

# -------------------------------
# Graph Display
# -------------------------------
elif menu == "📊 View Blood Sugar Graph":
    st.subheader("📊 Blood Sugar History")
    data = load_blood_sugar_history()
    plot_blood_sugar_graph(data)

# -------------------------------
# Health Tips
# -------------------------------
elif menu == "💡 Health Tips":
    st.subheader("💡 Health Tips for Managing Diabetes")
    tips = """
    ### Lifestyle & Dietary Tips:
    - 🥗 Eat balanced meals with low glycemic index foods
    - 🚶‍♂️ Exercise regularly (30 mins/day)
    - 💧 Stay hydrated and avoid sugary drinks
    - 🛏️ Get enough sleep (7-8 hrs)
    - 🧘‍♀️ Manage stress with mindfulness or yoga

    ### Monitoring Tips:
    - 📉 Monitor your blood sugar consistently
    - 💊 Take medications as prescribed
    - 📅 Schedule regular checkups with your doctor
    - 📔 Keep a log of readings, symptoms, and meals

    ⚠️ Always consult with your healthcare provider before making changes.
    """
    st.markdown(tips)

# End of App
