import streamlit as st
import requests
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore

FIREBASE_CREDENTIALS_PATH = "serviceAccountKey.json"
GEMINI_API_KEY = "AIzaSyDAlB1aWf6GFj1cORf1pI5oh9K_adYsXLg"
BLAND_API_KEY = 'sk-qbnjbnajvwoftvexd1s2t4cvhkqu9jm0o21ngj0bvy4wp3753y47req3yeb2nxgo69'

class AICallApp:
    def __init__(self):
        self._initialize_firebase()
        st.set_page_config(page_title="AI Conversation Hub", page_icon=":robot_face:", layout="wide")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! How can I assist you today?"}
            ]
        self.db = firestore.client()

    def _initialize_firebase(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Firebase initialization error: {e}")

    def run(self):
        st.title("AI Conversation Hub")
        col1, col2 = st.columns([3, 1])
        with col1:
            self._display_chat_history()
            if prompt := st.chat_input("Type your message..."):
                self._handle_user_message(prompt)
        with col2:
            self._render_call_configuration()

    def _display_chat_history(self):
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def _handle_user_message(self, prompt):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        self._generate_ai_response(prompt)

    def _generate_ai_response(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            ai_response = response.text
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(ai_response)
        except Exception as e:
            st.error(f"An error occurred: {e}")

    def _render_call_configuration(self):
        st.subheader("Initiate Call")
        phone_number = st.text_input("Enter Phone Number", placeholder="Enter the phone number without the country code (e.g., 9876543210)")
        task_description = st.text_area("Call Purpose", placeholder="Describe the purpose of the call...")
        default_voice = "nat"
        default_language = "en"
        default_max_duration = 12
        default_record_call = False
        default_wait_for_greeting = False
        if st.button("Start Call") and phone_number:
            complete_phone_number = f"+91{phone_number.strip()}"
            try:
                call_response = self._initiate_bland_call(
                    complete_phone_number, task_description, default_voice, default_language,
                    default_max_duration, default_record_call, default_wait_for_greeting
                )
                if call_response and isinstance(call_response, dict) and 'id' in call_response:
                    st.success(f"Call initiated successfully! Call ID: {call_response['id']}")
                else:
                    st.error("Failed to initiate call. Please check the Bland API response.")
            except Exception as e:
                st.error(f"Call initialization error: {e}")

    def _initiate_bland_call(self, phone_number, task, voice, language, max_duration, record, wait_for_greeting):
        headers = {
            'Authorization': BLAND_API_KEY,
            'Content-Type': 'application/json'
        }
        data = {
            "phone_number": phone_number,
            "task": task or "General conversational call",
            "model": "enhanced",
            "language": language,
            "voice": voice,
            "max_duration": max_duration,
            "record": record,
            "wait_for_greeting": wait_for_greeting,
            "voice_settings": {},
            "local_dialing": False,
            "answered_by_enabled": False,
            "interruption_threshold": 100
        }
        response = requests.post('https://api.bland.ai/v1/calls', json=data, headers=headers)
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                return {"error": "Invalid JSON in response"}
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}

def main():
    app = AICallApp()
    app.run()

if __name__ == "__main__":
    main()
