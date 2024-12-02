import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase

# Firebase Configuration
firebaseConfig = {
    "apiKey": "AIzaSyD9ma6Fqv-Su8JqiLt9QwscPR9wfm59y8s",
    "authDomain": "test-532d7.firebaseapp.com",
    "projectId": "test-532d7",
    "storageBucket": "test-532d7.firebasestorage.app",
    "messagingSenderId": "69079652948",
    "appId": "1:69079652948:web:ff78b18224ee4165e42bc1",
    "databaseURL": "https://test-532d7-default-rtdb.asia-southeast1.firebasedatabase.app"
}

# Initialize Firebase Admin SDK (for server-side operations)
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

# Initialize Pyrebase (for client-side authentication)
firebase = pyrebase.initialize_app(firebaseConfig)
auth_pyrebase = firebase.auth()

def signup():
    """Handle user signup process"""
    st.header("Sign Up")
   
    # Input fields
    username = st.text_input("Username", key="signup_username")
    email = st.text_input("Email", key="signup_email")
    phone_number = st.text_input("Phone Number (+country code)", key="signup_phone")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
   
    if st.button("Sign Up"):
        # Validate inputs
        if not username or not email or not phone_number or not password:
            st.error("Please fill in all fields")
            return
       
        if password != confirm_password:
            st.error("Passwords do not match")
            return
       
        try:
            # Create user in Firebase Authentication
            user = auth_pyrebase.create_user_with_email_and_password(email, password)
           
            # Update user profile with additional information
            user_info = {
                "username": username,
                "phone_number": phone_number,
                "email": email
            }
           
            # You can store additional user info in Realtime Database
            db = firebase.database()
            db.child("users").child(user['localId']).set(user_info)
           
            st.success("Account created successfully!")
       
        except Exception as e:
            st.error(f"Signup failed: {str(e)}")

def login():
    """Handle user login process"""
    st.header("Login")
   
    # Input fields
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
   
    if st.button("Login"):
        try:
            # Attempt to log in using Firebase Authentication
            user = auth_pyrebase.sign_in_with_email_and_password(email, password)
           
            # Store login state 
            st.session_state['user'] = user
            st.success("Logged in successfully!")
           
            # Optional: Retrieve additional user info
            db = firebase.database()
            user_info = db.child("users").child(user['localId']).get()
            
            if user_info:
                st.write(f"Welcome, {user_info.val()['username']}")
       
        except Exception as e:
            st.error(f"Login failed: {str(e)}")

def main():
    """Main Streamlit application"""
    st.title("Firebase Authentication")
   
    # Create tabs for Login and Signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
   
    with tab1:
        login()
   
    with tab2:
        signup()

# Run the Streamlit app
if __name__ == "__main__":
    main()