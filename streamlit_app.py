import streamlit as st
import pandas as pd
import plotly.express as px
import json
import hashlib
from pathlib import Path
from datetime import datetime

# ---------------- CONFIG ---------------- #

st.set_page_config(
    page_title="Smart Medical Assistance",
    page_icon="🏥",
    layout="wide"
)

USER_FILE = Path("users.json")

# ---------------- DATABASE ---------------- #

def load_users():
    if USER_FILE.exists():
        return json.loads(USER_FILE.read_text())
    return {}

def save_users(users):
    USER_FILE.write_text(json.dumps(users, indent=4))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- SESSION ---------------- #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- HOSPITAL DATA ---------------- #

hospital_data = pd.DataFrame({
    "Hospital":[
        "Apollo Hospital",
        "Fortis Hospital",
        "Global Hospital",
        "MIOT Hospital",
        "SIMS Hospital"
    ],
    "Location":[
        "Chennai",
        "Chennai",
        "Chennai",
        "Chennai",
        "Chennai"
    ],
    "Beds Available":[45,22,18,30,15],
    "Rating":[4.8,4.6,4.5,4.4,4.3]
})

# ---------------- DISEASE DATA ---------------- #

disease_map = {
    "fever":"Viral Fever",
    "cough":"Common Cold",
    "headache":"Migraine",
    "chest pain":"Cardiac Issue",
    "fatigue":"Anemia",
    "vomiting":"Food Poisoning",
    "breathing difficulty":"Respiratory Infection"
}

# ---------------- AUTH ---------------- #

def register_page():
    st.title("📝 Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):

        users = load_users()

        if username in users:
            st.error("User already exists")
        else:
            users[username] = hash_password(password)
            save_users(users)
            st.success("Registration Successful")

def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        users = load_users()

        if username in users and users[username] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------------- HOME ---------------- #

def home_page():

    st.title("🏥 Smart Medical Assistance System")

    st.markdown("""
    ### Features
    - Disease Prediction
    - Hospital Recommendation
    - Bed Availability
    - Medical Report Upload
    - Analytics Dashboard
    """)

    col1,col2,col3 = st.columns(3)

    col1.metric("Hospitals", 5)
    col2.metric("Available Beds", hospital_data["Beds Available"].sum())
    col3.metric("Users", len(load_users()))

# ---------------- DISEASE PREDICTION ---------------- #

def disease_prediction():

    st.title("🩺 Disease Prediction")

    symptom = st.text_input("Enter Symptom")

    if st.button("Predict Disease"):

        symptom = symptom.lower()

        disease = disease_map.get(
            symptom,
            "Consult a Doctor for Detailed Diagnosis"
        )

        st.success(f"Predicted Disease: {disease}")

# ---------------- HOSPITAL PAGE ---------------- #

def hospital_page():

    st.title("🏥 Nearby Hospitals")

    st.dataframe(
        hospital_data,
        use_container_width=True
    )

    fig = px.bar(
        hospital_data,
        x="Hospital",
        y="Beds Available",
        title="Available Beds"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------- REPORT UPLOAD ---------------- #

def reports_page():

    st.title("📄 Medical Reports")

    files = st.file_uploader(
        "Upload Reports",
        type=["pdf","png","jpg","jpeg"],
        accept_multiple_files=True
    )

    if files:

        for file in files:

            st.success(
                f"Uploaded: {file.name}"
            )

# ---------------- ANALYTICS ---------------- #

def analytics_page():

    st.title("📊 Analytics Dashboard")

    fig1 = px.pie(
        hospital_data,
        names="Hospital",
        values="Beds Available",
        title="Hospital Bed Distribution"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    fig2 = px.scatter(
        hospital_data,
        x="Beds Available",
        y="Rating",
        color="Hospital",
        size="Beds Available"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ---------------- PROFILE ---------------- #

def profile_page():

    st.title("👤 User Profile")

    st.write(
        f"Username: {st.session_state.username}"
    )

    st.write(
        f"Last Login: {datetime.now()}"
    )

# ---------------- MAIN APP ---------------- #

def app():

    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Select Page",
        [
            "Home",
            "Disease Prediction",
            "Hospitals",
            "Reports",
            "Analytics",
            "Profile"
        ]
    )

    if page == "Home":
        home_page()

    elif page == "Disease Prediction":
        disease_prediction()

    elif page == "Hospitals":
        hospital_page()

    elif page == "Reports":
        reports_page()

    elif page == "Analytics":
        analytics_page()

    elif page == "Profile":
        profile_page()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# ---------------- ENTRY ---------------- #

if not st.session_state.logged_in:

    option = st.sidebar.selectbox(
        "Choose",
        ["Login","Register"]
    )

    if option == "Login":
        login_page()
    else:
        register_page()

else:
    app()
