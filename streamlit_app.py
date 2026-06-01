from __future__ import annotations

import hashlib
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
USER_STORE_FILE = BASE_DIR / "users.json"

DEFAULT_USERS = {
    "patient@example.com": {
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "mobile": "9876543210",
        "name": "Aarav Sharma",
        "age": 34,
        "gender": "Male",
        "address": "Mumbai, Maharashtra",
        "insurance": "Care Secure Gold - ID CSG-20931",
        "history": ["Seasonal allergy", "Vitamin D deficiency"],
        "diagnoses": ["Mild allergic rhinitis - 2025", "Viral fever - 2024"],
    }
}

SYMPTOMS = [
    "Fever",
    "Cough",
    "Sore throat",
    "Headache",
    "Fatigue",
    "Body pain",
    "Shortness of breath",
    "Chest pain",
    "Nausea",
    "Vomiting",
    "Diarrhea",
    "Rash",
    "Joint pain",
    "Dizziness",
    "Loss of smell",
    "Abdominal pain",
]

DISEASES = {
    "Common Cold": {
        "symptoms": {"Cough", "Sore throat", "Headache", "Fatigue"},
        "specialist": "General Physician",
        "risk": "Low",
        "overview": "A common viral upper-respiratory infection that usually improves with supportive care.",
        "causes": "Respiratory viruses spread through droplets and close contact.",
        "risk_factors": "Crowded spaces, low immunity, poor sleep, and seasonal exposure.",
        "complications": "Sinusitis, ear infection, or worsening asthma in vulnerable patients.",
        "prevention": "Hand hygiene, masks in crowded spaces, rest, and avoiding close contact when sick.",
        "treatment": "Rest, hydration, steam inhalation, saline gargle, and physician-advised symptom relief.",
        "medications": "Paracetamol or antihistamines may be used only as advised by a clinician.",
        "diet": "Warm fluids, light meals, fruits, and adequate water.",
        "exercise": "Avoid intense exercise until fever and weakness resolve.",
        "timeline": "3 to 7 days for most people.",
        "cost": "Rs 500 - Rs 2,000",
        "success": "Very high with supportive care.",
    },
    "Influenza": {
        "symptoms": {"Fever", "Cough", "Sore throat", "Body pain", "Fatigue", "Headache"},
        "specialist": "General Physician",
        "risk": "Medium",
        "overview": "A contagious respiratory infection that can cause sudden fever, weakness, and body aches.",
        "causes": "Influenza virus infection.",
        "risk_factors": "Children, elderly adults, pregnancy, chronic illness, and low vaccination coverage.",
        "complications": "Pneumonia, dehydration, and worsening of chronic heart or lung disease.",
        "prevention": "Annual flu vaccination, hand hygiene, masks, and avoiding exposure during outbreaks.",
        "treatment": "Clinical evaluation, rest, hydration, fever control, and antivirals when prescribed early.",
        "medications": "Antivirals and fever reducers may be recommended by a doctor.",
        "diet": "Hydrating soups, oral fluids, soft foods, and electrolyte support when needed.",
        "exercise": "Rest until fever-free and energy returns.",
        "timeline": "5 to 10 days; fatigue may last longer.",
        "cost": "Rs 1,000 - Rs 6,000",
        "success": "High when treated early and monitored.",
    },
    "Dengue Suspected": {
        "symptoms": {"Fever", "Headache", "Body pain", "Rash", "Nausea", "Vomiting"},
        "specialist": "Internal Medicine",
        "risk": "High",
        "overview": "A mosquito-borne viral illness that requires platelet and hydration monitoring.",
        "causes": "Dengue virus transmitted by Aedes mosquitoes.",
        "risk_factors": "Mosquito exposure, stagnant water, and local outbreaks.",
        "complications": "Bleeding, shock, severe dehydration, and organ involvement.",
        "prevention": "Mosquito control, repellents, full-sleeve clothing, and removing stagnant water.",
        "treatment": "Urgent medical assessment, CBC monitoring, oral/IV fluids, and danger-sign surveillance.",
        "medications": "Avoid self-medicating with aspirin or ibuprofen; use only doctor-approved medicines.",
        "diet": "Fluids, oral rehydration, light meals, and clinician-advised nutrition.",
        "exercise": "Strict rest during fever and recovery.",
        "timeline": "7 to 14 days depending on severity.",
        "cost": "Rs 3,000 - Rs 40,000",
        "success": "Good with timely monitoring; severe cases need hospital care.",
    },
    "Gastroenteritis": {
        "symptoms": {"Nausea", "Vomiting", "Diarrhea", "Abdominal pain", "Fever", "Fatigue"},
        "specialist": "Gastroenterologist",
        "risk": "Medium",
        "overview": "Inflammation of the stomach and intestines causing loose stools, cramps, and dehydration risk.",
        "causes": "Contaminated food or water, viruses, bacteria, or parasites.",
        "risk_factors": "Unsafe water, outside food, poor hygiene, travel, and low immunity.",
        "complications": "Dehydration, electrolyte imbalance, and kidney stress in severe cases.",
        "prevention": "Safe drinking water, handwashing, cooked food, and food hygiene.",
        "treatment": "Oral rehydration, clinical review for severe symptoms, and targeted medicine when indicated.",
        "medications": "ORS is often useful; antibiotics only when prescribed.",
        "diet": "ORS, rice, bananas, curd, toast, soups, and small frequent meals.",
        "exercise": "Rest until hydration and strength normalize.",
        "timeline": "2 to 5 days for mild cases.",
        "cost": "Rs 800 - Rs 8,000",
        "success": "High with hydration and timely care.",
    },
    "Cardiac Warning Signs": {
        "symptoms": {"Chest pain", "Shortness of breath", "Dizziness", "Fatigue"},
        "specialist": "Cardiologist",
        "risk": "Emergency",
        "overview": "Chest pain with breathlessness or dizziness can indicate a serious heart-related emergency.",
        "causes": "Possible reduced blood flow to the heart, rhythm issues, or other urgent conditions.",
        "risk_factors": "Diabetes, hypertension, smoking, family history, high cholesterol, and older age.",
        "complications": "Heart attack, arrhythmia, shock, or sudden deterioration.",
        "prevention": "Regular screening, BP control, diabetes care, exercise, and smoking cessation.",
        "treatment": "Seek emergency medical care immediately. Do not delay for app-based assessment.",
        "medications": "Emergency medicines must be clinician-directed.",
        "diet": "After medical clearance, heart-healthy low-salt nutrition may be recommended.",
        "exercise": "Do not exercise during symptoms. Resume only after medical clearance.",
        "timeline": "Immediate assessment is required.",
        "cost": "Rs 5,000 - Rs 2,00,000+",
        "success": "Best when emergency treatment is immediate.",
    },
}

HOSPITALS = [
    {
        "name": "CityCare Multispeciality Hospital",
        "location": "Andheri East",
        "distance": 2.4,
        "beds": 42,
        "total_beds": 160,
        "icu": 8,
        "emergency": True,
        "ventilators": 5,
        "rating": 4.6,
        "fee": 900,
        "phone": "022-4000-1212",
        "specialists": ["General Physician", "Cardiologist", "Internal Medicine"],
    },
    {
        "name": "Metro Heart & Trauma Centre",
        "location": "Bandra Kurla Complex",
        "distance": 5.1,
        "beds": 18,
        "total_beds": 120,
        "icu": 3,
        "emergency": True,
        "ventilators": 2,
        "rating": 4.8,
        "fee": 1400,
        "phone": "022-4111-2020",
        "specialists": ["Cardiologist", "Emergency Medicine", "Neurologist"],
    },
    {
        "name": "GreenLife General Hospital",
        "location": "Powai",
        "distance": 6.8,
        "beds": 64,
        "total_beds": 190,
        "icu": 12,
        "emergency": True,
        "ventilators": 7,
        "rating": 4.4,
        "fee": 700,
        "phone": "022-4222-8899",
        "specialists": ["General Physician", "Gastroenterologist", "Pediatrician"],
    },
    {
        "name": "Sunrise Infectious Disease Clinic",
        "location": "Dadar",
        "distance": 8.3,
        "beds": 9,
        "total_beds": 70,
        "icu": 1,
        "emergency": False,
        "ventilators": 1,
        "rating": 4.2,
        "fee": 650,
        "phone": "022-4555-3333",
        "specialists": ["Internal Medicine", "General Physician"],
    },
]


def ensure_state() -> None:
    defaults = {
        "page": "Home",
        "logged_in": False,
        "user": None,
        "captcha": str(random.randint(1000, 9999)),
        "appointments": [],
        "reports": [],
        "alerts": [
            "Annual health checkup due this month",
            "CityCare has 42 beds available nearby",
            "Drink water regularly during high-temperature days",
        ],
        "audit_logs": ["System initialized", "Security scan completed"],
        "theme": "Light",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def set_page(page: str) -> None:
    st.session_state.page = page


def password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> dict[str, dict[str, Any]]:
    if not USER_STORE_FILE.exists():
        save_users(DEFAULT_USERS)
        return DEFAULT_USERS.copy()

    try:
        users = json.loads(USER_STORE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        users = {}

    if not isinstance(users, dict):
        users = {}

    merged = DEFAULT_USERS.copy()
    for email, user in users.items():
        if isinstance(email, str) and isinstance(user, dict):
            merged[email.lower()] = user
    return merged


def save_users(users: dict[str, dict[str, Any]]) -> None:
    USER_STORE_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")


def save_registered_user(email: str, user: dict[str, Any]) -> None:
    users = load_users()
    users[email.lower()] = user
    save_users(users)


def auth_user(email: str, password: str) -> tuple[bool, str]:
    normalized_email = email.strip().lower()
    user = load_users().get(normalized_email)
    if user and user["password_hash"] == password_hash(password):
        st.session_state.setdefault("audit_logs", [])
        st.session_state.logged_in = True
        st.session_state.user = {**user, "email": normalized_email}
        st.session_state.audit_logs.append(f"Login success: {normalized_email} at {datetime.now().strftime('%H:%M')}")
        return True, "Login successful."
    return False, "Invalid email or password."


def risk_color(risk: str) -> str:
    return {
        "Low": "#0f766e",
        "Medium": "#d97706",
        "High": "#dc2626",
        "Emergency": "#991b1b",
    }.get(risk, "#334155")


def bed_status(beds: int, total: int) -> tuple[str, str]:
    ratio = beds / total if total else 0
    if beds == 0 or ratio < 0.08:
        return "Full", "#dc2626"
    if ratio < 0.25:
        return "Limited", "#d97706"
    return "Available", "#16a34a"


def predict_disease(selected_symptoms: list[str], severity: int) -> dict[str, Any]:
    if not selected_symptoms:
        disease_name = "Common Cold"
        match_score = 0
    else:
        selected = set(selected_symptoms)
        disease_name = max(
            DISEASES,
            key=lambda name: len(selected & DISEASES[name]["symptoms"]) / max(len(DISEASES[name]["symptoms"]), 1),
        )
        disease = DISEASES[disease_name]
        match_score = len(selected & disease["symptoms"]) / max(len(disease["symptoms"]), 1)

    disease = DISEASES[disease_name]
    confidence = min(96, round((match_score * 72) + (severity * 2.4) + 12))
    severity_score = min(100, round(severity * 10 + confidence * 0.35))
    recommended_action = "Book a doctor consultation"
    if disease["risk"] == "Emergency" or severity >= 8:
        recommended_action = "Seek urgent/emergency medical care now"
    elif disease["risk"] == "High" or severity >= 6:
        recommended_action = "Consult a physician within 24 hours"

    return {
        "name": disease_name,
        "confidence": confidence,
        "severity_score": severity_score,
        "recommended_action": recommended_action,
        **disease,
    }


def hospital_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Hospital": hospital["name"],
                "Location": hospital["location"],
                "Distance km": hospital["distance"],
                "Rating": hospital["rating"],
                "Available beds": hospital["beds"],
                "ICU beds": hospital["icu"],
                "Ventilators": hospital["ventilators"],
                "Emergency": "Yes" if hospital["emergency"] else "No",
                "Consultation fee": f"Rs {hospital['fee']}",
                "Contact": hospital["phone"],
            }
            for hospital in HOSPITALS
        ]
    )


def style_app() -> None:
    dark = st.session_state.theme == "Dark"
    background = "#08111f" if dark else "#eef7fb"
    surface = "#111c2e" if dark else "#ffffff"
    soft_surface = "#14243a" if dark else "#f8fcff"
    text = "#ecf5ff" if dark else "#102033"
    muted = "#a8bad1" if dark else "#5e7087"
    line = "#29415c" if dark else "#d8e7ef"
    button_text = "#ffffff" if dark else "#0f2f3c"

    st.markdown(
        f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
          html, body, [class*="css"] {{
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          }}
          .stApp {{
            background:
              radial-gradient(circle at 18% 0%, rgba(45, 212, 191, 0.18), transparent 34rem),
              radial-gradient(circle at 92% 12%, rgba(56, 189, 248, 0.16), transparent 30rem),
              linear-gradient(180deg, {background} 0%, {background} 100%);
            color: {text};
          }}
          .main .block-container {{
            padding-top: 1.15rem;
            padding-bottom: 2.4rem;
            max-width: 1280px;
          }}
          h1, h2, h3 {{
            letter-spacing: 0 !important;
            color: {text};
          }}
          h1 {{
            font-weight: 800 !important;
          }}
          .stSidebar {{
            background: {surface};
            border-right: 1px solid {line};
          }}
          [data-testid="stMetric"], .care-card {{
            background: {surface};
            border: 1px solid {line};
            border-radius: 18px;
            padding: 1.05rem;
            box-shadow: 0 18px 46px rgba(15, 23, 42, 0.09);
          }}
          [data-testid="stMetric"] {{
            border-left: 4px solid #14b8a6;
          }}
          [data-testid="stMetricValue"] {{
            font-size: 1.45rem;
            font-weight: 800;
          }}
          .hero {{
            min-height: 430px;
            border-radius: 24px;
            padding: 3.4rem 2.6rem;
            background:
              linear-gradient(90deg, rgba(4, 47, 46, 0.92), rgba(14, 116, 144, 0.75), rgba(12, 74, 110, 0.46)),
              url("https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1600&q=80");
            background-size: cover;
            background-position: center;
            color: white;
            display: flex;
            align-items: center;
            position: relative;
            overflow: hidden;
            box-shadow: 0 28px 80px rgba(15, 23, 42, 0.22);
          }}
          .hero:after {{
            content: "";
            position: absolute;
            inset: auto 2rem 2rem auto;
            width: 230px;
            height: 230px;
            border: 1px solid rgba(255, 255, 255, .22);
            border-radius: 999px;
          }}
          .hero-content {{
            position: relative;
            z-index: 1;
          }}
          .hero h1 {{
            color: white;
            max-width: 780px;
            font-size: clamp(2rem, 5vw, 4rem);
            line-height: 1.05;
            margin: 0 0 1rem 0;
          }}
          .hero p {{
            color: rgba(255,255,255,.92);
            max-width: 680px;
            font-size: 1.08rem;
            line-height: 1.7;
          }}
          .muted {{
            color: {muted};
          }}
          .hero-actions {{
            display: flex;
            gap: .8rem;
            margin-top: 1.4rem;
            flex-wrap: wrap;
          }}
          .hero-stat-row {{
            display: flex;
            gap: .75rem;
            flex-wrap: wrap;
            margin-top: 1.8rem;
          }}
          .hero-stat {{
            min-width: 130px;
            background: rgba(255,255,255,.14);
            border: 1px solid rgba(255,255,255,.24);
            border-radius: 16px;
            padding: .85rem 1rem;
            backdrop-filter: blur(10px);
          }}
          .hero-stat b {{
            display: block;
            font-size: 1.35rem;
            color: white;
          }}
          .hero-stat span {{
            color: rgba(255,255,255,.78);
            font-size: .82rem;
          }}
          .section-kicker {{
            color: #0891b2;
            text-transform: uppercase;
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .08em;
            margin-bottom: .2rem;
          }}
          .banner {{
            background: {"#102b3c" if dark else "#ecfeff"};
            color: {"#d7f9ff" if dark else "#164e63"};
            border: 1px solid {"#155e75" if dark else "#a5f3fc"};
            padding: 1rem 1.1rem;
            border-radius: 16px;
            margin: 1rem 0;
          }}
          .emergency {{
            background: {"#3b121b" if dark else "#fff1f2"};
            color: {"#fecdd3" if dark else "#9f1239"};
            border: 1px solid {"#881337" if dark else "#fecdd3"};
            padding: 1rem 1.1rem;
            border-radius: 16px;
            margin: 1rem 0;
            font-weight: 700;
          }}
          .pill {{
            display: inline-block;
            padding: .35rem .7rem;
            border-radius: 999px;
            background: rgba(224, 242, 254, .95);
            color: #075985;
            font-size: .82rem;
            font-weight: 700;
          }}
          .feature-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin: 1.2rem 0 1.4rem;
          }}
          .feature-card {{
            background: {surface};
            border: 1px solid {line};
            border-radius: 18px;
            padding: 1.05rem;
            min-height: 150px;
            box-shadow: 0 14px 42px rgba(15, 23, 42, .08);
          }}
          .feature-icon {{
            width: 40px;
            height: 40px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, #14b8a6, #38bdf8);
            color: white;
            font-weight: 800;
            margin-bottom: .75rem;
          }}
          .feature-card h3 {{
            font-size: 1rem;
            margin: 0 0 .35rem 0;
          }}
          .feature-card p {{
            color: {muted};
            margin: 0;
            line-height: 1.55;
            font-size: .92rem;
          }}
          .hospital-card h3 {{
            font-size: 1.04rem;
            margin: 0 0 .35rem;
          }}
          .hospital-meta {{
            display: flex;
            justify-content: space-between;
            gap: .6rem;
            margin: .7rem 0;
          }}
          .hospital-meta span {{
            display: block;
            background: {soft_surface};
            border: 1px solid {line};
            border-radius: 12px;
            padding: .55rem;
            flex: 1;
            font-size: .85rem;
          }}
          .status-dot {{
            display: inline-block;
            width: .6rem;
            height: .6rem;
            border-radius: 50%;
            margin-right: .35rem;
          }}
          .footer {{
            border-top: 1px solid {line};
            margin-top: 2rem;
            padding-top: 1rem;
            color: {muted};
            font-size: .9rem;
          }}
          .nav-button button {{
            border-radius: 8px !important;
          }}
          .stButton > button {{
            border-radius: 12px;
            border: 1px solid {line};
            color: {button_text};
            font-weight: 700;
          }}
          .stButton > button[kind="primary"], .stFormSubmitButton button[kind="primary"] {{
            background: linear-gradient(135deg, #0f766e, #0284c7);
            color: white;
            border: 0;
          }}
          div[data-testid="stDataFrame"] {{
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid {line};
          }}
          @media (max-width: 900px) {{
            .feature-grid {{
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
            .hero {{
              padding: 2.4rem 1.4rem;
            }}
          }}
          @media (max-width: 560px) {{
            .feature-grid {{
              grid-template-columns: 1fr;
            }}
            .hero-stat {{
              min-width: 100%;
            }}
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def nav() -> None:
    st.session_state.theme = st.sidebar.radio("Theme", ["Light", "Dark"], horizontal=True)
    st.sidebar.title("General Smart Medical Assistance")
    pages = ["Home"]
    if st.session_state.logged_in:
        pages += [
            "Dashboard",
            "Disease Prediction",
            "Disease Library",
            "Hospitals & Beds",
            "Appointments",
            "Reports",
            "Notifications",
            "Admin",
            "Analytics",
        ]
    else:
        pages += ["Login", "Register", "About", "Contact"]
    for page in pages:
        if st.sidebar.button(page, width="stretch", key=f"nav_{page}"):
            set_page(page)
    if st.session_state.logged_in:
        st.sidebar.divider()
        st.sidebar.success(f"Signed in as {st.session_state.user['name']}")
        if st.sidebar.button("Logout", width="stretch"):
            st.session_state.logged_in = False
            st.session_state.user = None
            set_page("Home")
            st.rerun()


def render_hospital_cards(limit: int | None = None, specialist: str | None = None) -> None:
    hospitals = HOSPITALS
    if specialist:
        hospitals = [hospital for hospital in hospitals if specialist in hospital["specialists"]] or HOSPITALS
    if limit:
        hospitals = hospitals[:limit]
    cols = st.columns(min(3, len(hospitals)))
    for index, hospital in enumerate(hospitals):
        status, color = bed_status(hospital["beds"], hospital["total_beds"])
        with cols[index % len(cols)]:
            st.markdown(
                f"""
                <div class="care-card hospital-card">
                  <h3>{hospital['name']}</h3>
                  <p class="muted">{hospital['location']} - {hospital['distance']} km away</p>
                  <div class="hospital-meta">
                    <span><b>{hospital['beds']}</b><br>Available beds</span>
                    <span><b>{hospital['icu']}</b><br>ICU beds</span>
                    <span><b>{hospital['rating']}</b><br>Rating</span>
                  </div>
                  <p><span class="status-dot" style="background:{color};"></span><b style="color:{color};">{status}</b> capacity</p>
                  <p><b>Contact:</b> {hospital['phone']}</p>
                  <p><b>Emergency:</b> {'24/7 available' if hospital['emergency'] else 'Not available'}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def home_page() -> None:
    st.markdown(
        """
        <section class="hero">
          <div class="hero-content">
            <span class="pill">Official Web Application</span>
            <h1>General Smart Medical Assistance System</h1>
            <p>Identify possible health conditions from symptoms, review treatment guidance, find hospitals, monitor bed availability, and manage appointments from one secure dashboard.</p>
            <div class="hero-stat-row">
              <div class="hero-stat"><b>24/7</b><span>Emergency guidance</span></div>
              <div class="hero-stat"><b>4</b><span>Nearby hospitals</span></div>
              <div class="hero-stat"><b>133</b><span>Open beds tracked</span></div>
              <div class="hero-stat"><b>5</b><span>Disease pathways</span></div>
            </div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="emergency">Emergency support: Call local emergency services immediately for chest pain, severe breathing difficulty, stroke symptoms, major injury, or loss of consciousness.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="banner">Healthcare awareness: This app supports triage and education only. It does not replace a licensed medical professional.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("Login", type="primary", width="stretch"):
            set_page("Login")
            st.rerun()
    with c2:
        if st.button("Register", width="stretch"):
            set_page("Register")
            st.rerun()
    with c3:
        st.info("Demo credentials: patient@example.com / demo123")

    st.markdown(
        """
        <div class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon">01</div>
            <h3>Symptom Intelligence</h3>
            <p>Structured symptom entry, severity scoring, and triage-style prediction results.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">02</div>
            <h3>Hospital Matching</h3>
            <p>Compare nearby hospitals by specialty, distance, ratings, beds, and emergency support.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">03</div>
            <h3>Care Coordination</h3>
            <p>Book appointments, upload reports, review alerts, and keep patient records together.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">04</div>
            <h3>Admin Analytics</h3>
            <p>Monitor bed occupancy, disease trends, appointment activity, and audit events.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-kicker">Nearby care network</div>', unsafe_allow_html=True)
    st.subheader("Nearby Hospitals")
    render_hospital_cards()

    col_about, col_contact = st.columns(2)
    with col_about:
        st.subheader("About Us")
        st.write(
            "We provide a smart healthcare workflow for symptom triage, hospital matching, bed visibility, appointments, records, and analytics."
        )
    with col_contact:
        st.subheader("Contact")
        st.write("Care desk: care@example.org")
        st.write("Support: +91 98765 43210")
    st.markdown('<div class="footer">Privacy-first healthcare assistance platform. Always consult a doctor for diagnosis and treatment.</div>', unsafe_allow_html=True)


def login_page() -> None:
    st.title("Secure Login")
    st.caption("Use your registered email and password.")
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="patient@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary")
    if submitted:
        ok, message = auth_user(email, password)
        if ok:
            st.success(message)
            set_page("Dashboard")
            st.rerun()
        else:
            st.error(message)
    if st.button("Forgot password"):
        st.info("Password reset workflow would send a secure reset link to your registered email.")


def register_page() -> None:
    st.title("Patient Registration")
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        full_name = col1.text_input("Full name")
        age = col2.number_input("Age", min_value=1, max_value=120, value=30)
        gender = col1.selectbox("Gender", ["Female", "Male", "Other", "Prefer not to say"])
        email = col2.text_input("Email")
        mobile = col1.text_input("Mobile number")
        address = col2.text_area("Address")
        password = col1.text_input("Create password", type="password")
        otp = col2.text_input("OTP verification", placeholder="Use 123456 for demo")
        submitted = st.form_submit_button("Create account", type="primary")
    if submitted:
        if otp != "123456":
            st.error("OTP verification failed. Use 123456 in this demo.")
        elif not full_name or not email or not mobile or not password:
            st.error("Please complete all required fields.")
        else:
            save_registered_user(email, {
                "password_hash": password_hash(password),
                "mobile": mobile,
                "name": full_name,
                "age": age,
                "gender": gender,
                "address": address,
                "insurance": "Not added",
                "history": [],
                "diagnoses": [],
            })
            st.success("Registration completed. Please login.")
            set_page("Login")


def require_login() -> bool:
    if not st.session_state.logged_in:
        st.warning("Please login to access this section.")
        if st.button("Go to Login"):
            set_page("Login")
            st.rerun()
        return False
    return True


def dashboard_page() -> None:
    if not require_login():
        return
    user = st.session_state.user
    st.title("Patient Dashboard")
    st.caption("Personal health overview, profile, records, statistics, and alerts.")
    cols = st.columns(5)
    cols[0].metric("Health score", "82/100", "+4")
    cols[1].metric("Recent diagnoses", len(user["diagnoses"]))
    cols[2].metric("Upcoming appointments", len(st.session_state.appointments))
    cols[3].metric("Nearby hospitals", len(HOSPITALS))
    cols[4].metric("Bed alerts", "2")

    profile, records = st.columns([1, 1.2])
    with profile:
        st.subheader("Patient Profile")
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Age/Gender:** {user['age']} / {user['gender']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Mobile:** {user['mobile']}")
        st.write(f"**Address:** {user['address']}")
        st.write(f"**Insurance:** {user['insurance']}")
    with records:
        st.subheader("Medical History")
        st.write(user["history"] or ["No history added"])
        st.subheader("Previous Diagnoses")
        st.write(user["diagnoses"] or ["No previous diagnoses"])
        st.subheader("Emergency Contacts")
        st.write("Primary: +91 98765 43210")
        st.write("Ambulance: 108")

    st.subheader("Bed Availability Snapshot")
    render_bed_chart()


def prediction_page() -> None:
    if not require_login():
        return
    st.title("Disease Prediction")
    st.caption("Enter symptoms to receive triage-style assistance. This is not a diagnosis.")
    selected = st.multiselect("Search and select symptoms", SYMPTOMS)
    voice_text = st.text_area("Voice symptom input transcript", placeholder="Example: I have fever, cough, and body pain")
    severity = st.slider("Symptom severity", 1, 10, 5)
    if voice_text:
        selected = sorted(set(selected + [symptom for symptom in SYMPTOMS if symptom.lower() in voice_text.lower()]))
        st.caption(f"Detected symptoms from transcript: {', '.join(selected) if selected else 'None'}")

    if st.button("Predict Possible Condition", type="primary"):
        result = predict_disease(selected, severity)
        st.session_state.last_prediction = result
    result = st.session_state.get("last_prediction")
    if not result:
        return

    color = risk_color(result["risk"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Predicted disease", result["name"])
    c2.metric("Confidence", f"{result['confidence']}%")
    c3.markdown(f"<div class='care-card'><b>Risk level</b><h3 style='color:{color};'>{result['risk']}</h3></div>", unsafe_allow_html=True)
    c4.metric("Severity score", f"{result['severity_score']}/100")

    st.error(result["recommended_action"]) if result["risk"] in {"High", "Emergency"} else st.info(result["recommended_action"])
    st.write(f"**Suggested specialist:** {result['specialist']}")
    st.write("**Immediate precautions:** Avoid self-medication, stay hydrated when appropriate, monitor warning signs, and consult a licensed clinician.")

    st.subheader("Disease Analysis")
    sections = ["overview", "causes", "risk_factors", "complications", "prevention", "timeline"]
    for section in sections:
        st.write(f"**{section.replace('_', ' ').title()}:** {result[section]}")

    st.subheader("Treatment Recommendation")
    st.write(f"**Required treatment:** {result['treatment']}")
    st.write(f"**Estimated duration:** {result['timeline']}")
    st.write(f"**Approximate cost:** {result['cost']}")
    st.write(f"**Recovery probability:** {result['success']}")
    st.write(f"**Home care:** Rest, follow clinician instructions, track temperature and symptoms.")
    st.write(f"**Diet:** {result['diet']}")
    st.write(f"**Exercise:** {result['exercise']}")

    st.subheader("Recommended Hospitals")
    render_hospital_cards(specialist=result["specialist"])


def disease_library_page() -> None:
    if not require_login():
        return
    st.title("Disease Information Library")
    disease_name = st.selectbox("Select disease", list(DISEASES))
    disease = DISEASES[disease_name]
    st.subheader(disease_name)
    st.write(f"**Medical description:** {disease['overview']}")
    st.write(f"**Causes:** {disease['causes']}")
    st.write(f"**Symptoms:** {', '.join(sorted(disease['symptoms']))}")
    st.write("**Diagnosis methods:** Physical exam, symptom history, vitals, lab tests or imaging when indicated.")
    st.write(f"**Treatment procedures:** {disease['treatment']}")
    st.write(f"**Required medications:** {disease['medications']}")
    st.write(f"**Lifestyle recommendations:** {disease['diet']} {disease['exercise']}")
    st.write(f"**Prevention techniques:** {disease['prevention']}")
    st.write(f"**Recovery process:** {disease['timeline']}")
    st.write(f"**Success rate:** {disease['success']}")
    with st.expander("Frequently asked questions"):
        st.write("**Can this app diagnose me?** No. It provides triage guidance only.")
        st.write("**When should I seek urgent care?** Severe chest pain, breathing difficulty, fainting, severe dehydration, bleeding, or worsening symptoms.")
        st.write("**Should I take medicines listed here?** Only after consulting a licensed clinician.")


def render_bed_chart() -> None:
    beds = pd.DataFrame(
        [
            {
                "Hospital": h["name"],
                "Available": h["beds"],
                "Occupied": h["total_beds"] - h["beds"],
                "ICU": h["icu"],
                "Emergency": 10 if h["emergency"] else 0,
                "Ventilators": h["ventilators"],
            }
            for h in HOSPITALS
        ]
    )
    figure = go.Figure()
    figure.add_bar(x=beds["Hospital"], y=beds["Available"], name="Available", marker_color="#16a34a")
    figure.add_bar(x=beds["Hospital"], y=beds["Occupied"], name="Occupied", marker_color="#94a3b8")
    figure.update_layout(height=360, barmode="stack", margin={"l": 0, "r": 0, "t": 20, "b": 0})
    st.plotly_chart(figure, width="stretch")


def hospitals_page() -> None:
    if not require_login():
        return
    st.title("Hospital Recommendation & Bed Availability")
    specialist = st.selectbox("Filter by specialization", ["All"] + sorted({s for h in HOSPITALS for s in h["specialists"]}))
    filtered = HOSPITALS if specialist == "All" else [h for h in HOSPITALS if specialist in h["specialists"]]
    st.dataframe(hospital_frame()[hospital_frame()["Hospital"].isin([h["name"] for h in filtered])], width="stretch", hide_index=True)
    st.subheader("Real-Time Bed Dashboard")
    for hospital in filtered:
        status, color = bed_status(hospital["beds"], hospital["total_beds"])
        st.markdown(
            f"<div class='care-card'><b>{hospital['name']}</b> - <span style='color:{color};font-weight:800;'>{status}</span><br>Total beds: {hospital['total_beds']} | Available: {hospital['beds']} | Occupied: {hospital['total_beds'] - hospital['beds']} | ICU: {hospital['icu']} | Emergency beds: {'Available' if hospital['emergency'] else 'Unavailable'} | Ventilators: {hospital['ventilators']}</div>",
            unsafe_allow_html=True,
        )
    render_bed_chart()


def appointments_page() -> None:
    if not require_login():
        return
    st.title("Appointment Booking")
    with st.form("appointment_form"):
        hospital = st.selectbox("Select hospital", [h["name"] for h in HOSPITALS])
        specialists = next(h["specialists"] for h in HOSPITALS if h["name"] == hospital)
        doctor_type = st.selectbox("Select doctor", [f"Dr. {name} - {spec}" for name, spec in zip(["Meera Rao", "Kabir Sen", "Nisha Iyer"], specialists * 2)])
        appt_date = st.date_input("Select date", min_value=date.today(), value=date.today() + timedelta(days=1))
        slot = st.selectbox("Select time slot", ["09:00 AM", "11:30 AM", "02:00 PM", "05:00 PM"])
        submitted = st.form_submit_button("Book appointment", type="primary")
    if submitted:
        confirmation = {
            "Hospital": hospital,
            "Doctor": doctor_type,
            "Date": str(appt_date),
            "Time": slot,
            "Status": "Confirmed",
        }
        st.session_state.appointments.append(confirmation)
        st.session_state.alerts.append(f"Appointment confirmed at {hospital} on {appt_date} {slot}")
        st.success("Appointment confirmed.")
    if st.session_state.appointments:
        st.dataframe(pd.DataFrame(st.session_state.appointments), width="stretch", hide_index=True)


def reports_page() -> None:
    if not require_login():
        return
    st.title("Medical Reports")
    uploads = st.file_uploader("Upload medical reports or lab results", accept_multiple_files=True, type=["pdf", "png", "jpg", "jpeg", "csv"])
    for upload in uploads:
        st.session_state.reports.append({"File": upload.name, "Uploaded": datetime.now().strftime("%Y-%m-%d %H:%M")})
    if st.session_state.reports:
        st.dataframe(pd.DataFrame(st.session_state.reports).drop_duplicates(), width="stretch", hide_index=True)
        summary = "Health summary: Patient records uploaded for clinician review. Recent vitals and reports should be interpreted by a licensed medical professional."
        st.download_button("Download health summary", summary, file_name="health_summary.txt")
    else:
        st.info("No reports uploaded yet.")


def notifications_page() -> None:
    if not require_login():
        return
    st.title("Notifications & Emergency Assistance")
    e1, e2, e3 = st.columns(3)
    if e1.button("One-click emergency support", type="primary", width="stretch"):
        st.error("Emergency support triggered. Call local emergency services immediately.")
    if e2.button("Request ambulance", width="stretch"):
        st.warning("Ambulance request workflow started. Confirm location with emergency operator.")
    if e3.button("Share live location", width="stretch"):
        st.info("Live location sharing would open secure consent-based sharing in production.")

    st.subheader("Alerts")
    for alert in st.session_state.alerts:
        st.info(alert)
    st.subheader("Nearest Emergency Hospitals")
    render_hospital_cards(limit=2)


def admin_page() -> None:
    if not require_login():
        return
    st.title("Admin Panel")
    st.caption("Role-based administration prototype for hospitals, doctors, patients, beds, appointments, analytics, and disease data.")
    tabs = st.tabs(["Hospitals", "Doctors", "Patients", "Beds", "Appointments", "Disease DB", "Audit Logs"])
    with tabs[0]:
        st.dataframe(hospital_frame(), width="stretch", hide_index=True)
    with tabs[1]:
        st.dataframe(
            pd.DataFrame(
                [
                    {"Doctor": "Dr. Meera Rao", "Specialization": "General Physician", "Hospital": "CityCare"},
                    {"Doctor": "Dr. Kabir Sen", "Specialization": "Cardiologist", "Hospital": "Metro Heart"},
                    {"Doctor": "Dr. Nisha Iyer", "Specialization": "Internal Medicine", "Hospital": "GreenLife"},
                ]
            ),
            width="stretch",
            hide_index=True,
        )
    with tabs[2]:
        st.write("Patient management would include verification, consent, access roles, and record permissions.")
    with tabs[3]:
        hospital = st.selectbox("Update hospital bed availability", [h["name"] for h in HOSPITALS])
        new_beds = st.number_input("Available beds", min_value=0, max_value=300, value=20)
        if st.button("Save bed update"):
            st.success(f"Saved demo update for {hospital}: {new_beds} beds.")
    with tabs[4]:
        st.dataframe(pd.DataFrame(st.session_state.appointments), width="stretch", hide_index=True)
    with tabs[5]:
        st.dataframe(pd.DataFrame([{"Disease": name, "Risk": d["risk"], "Specialist": d["specialist"]} for name, d in DISEASES.items()]), width="stretch", hide_index=True)
    with tabs[6]:
        for log in st.session_state.audit_logs:
            st.code(log)


def analytics_page() -> None:
    if not require_login():
        return
    st.title("Analytics Dashboard")
    disease_trends = pd.DataFrame(
        {
            "Disease": ["Common Cold", "Influenza", "Dengue Suspected", "Gastroenteritis", "Cardiac Warning Signs"],
            "Cases": [122, 88, 37, 64, 18],
            "Recovery": [96, 91, 84, 93, 72],
            "Region": ["West", "West", "South", "North", "Central"],
        }
    )
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(disease_trends, x="Disease", y="Cases", color="Region", title="Disease Trends"), width="stretch")
    with c2:
        st.plotly_chart(px.pie(disease_trends, names="Disease", values="Cases", title="Regional Disease Analysis"), width="stretch")
    occupancy = pd.DataFrame(
        [{"Hospital": h["name"], "Occupancy %": round(((h["total_beds"] - h["beds"]) / h["total_beds"]) * 100, 1)} for h in HOSPITALS]
    )
    st.plotly_chart(px.line(occupancy, x="Hospital", y="Occupancy %", markers=True, title="Hospital Occupancy Rate"), width="stretch")
    stats = st.columns(4)
    stats[0].metric("Patient statistics", "1,284")
    stats[1].metric("Appointments", "312")
    stats[2].metric("Recovery avg", "89%")
    stats[3].metric("Active alerts", len(st.session_state.alerts))


def about_page() -> None:
    st.title("About Us")
    st.write("General Smart Medical Assistance System is a prototype healthcare ecosystem for patient triage, hospital discovery, bed visibility, appointment management, reports, notifications, admin operations, and analytics.")
    st.write("Security design includes role-based access, audit logs, privacy-first forms, encrypted transport expectations, and consent-aware workflows for production implementation.")


def contact_page() -> None:
    st.title("Contact")
    st.write("Care desk: care@example.org")
    st.write("Emergency: call local emergency services immediately.")
    st.text_area("Message")
    if st.button("Submit"):
        st.success("Message submitted in demo mode.")


def main() -> None:
    ensure_state()
    style_app()
    nav()
    page = st.session_state.page
    if page == "Home":
        home_page()
    elif page == "Login":
        login_page()
    elif page == "Register":
        register_page()
    elif page == "Dashboard":
        dashboard_page()
    elif page == "Disease Prediction":
        prediction_page()
    elif page == "Disease Library":
        disease_library_page()
    elif page == "Hospitals & Beds":
        hospitals_page()
    elif page == "Appointments":
        appointments_page()
    elif page == "Reports":
        reports_page()
    elif page == "Notifications":
        notifications_page()
    elif page == "Admin":
        admin_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "About":
        about_page()
    elif page == "Contact":
        contact_page()


if __name__ == "__main__":
    main()
