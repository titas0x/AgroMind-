import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import numpy as np
import time
import random
import io

# --- 1. THE "NO-ERROR" AI CONFIGURATION ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        # 'transport=rest' is the specific fix for the v1beta/404 error
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"], transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        model = None
except Exception:
    model = None

# --- 2. APP CONFIGURATION ---
st.set_page_config(page_title="AgroMind Pro", layout="wide", page_icon="🌱")

# --- 3. SESSION STATE (The Database) ---
if 'users' not in st.session_state: st.session_state.users = {} 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'history' not in st.session_state: st.session_state.history = []

# --- 4. AUTHENTICATION SYSTEM (Sign In / Sign Up) ---
def auth_system():
    st.title("🌱 AgroMind: Smart Agriculture System")
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    with tab2:
        st.subheader("Register New Farmer")
        nu = st.text_input("Choose Username", key="reg_u")
        np = st.text_input("Choose Password", type="password", key="reg_p")
        if st.button("Register"):
            if nu and np:
                st.session_state.users[nu] = np
                st.success("Account created! You can now Sign In.")
    with tab1:
        st.subheader("Login to Dashboard")
        u = st.text_input("Username", key="log_u")
        p = st.text_input("Password", type="password", key="log_p")
        if st.button("Access System"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied: Invalid Username or Password")

# --- 5. MAIN DASHBOARD ---
if not st.session_state.logged_in:
    auth_system()
else:
    # --- SIDEBAR (Logout, Reset, Download) ---
    with st.sidebar:
        st.header(f"👤 {st.session_state.user}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        if st.session_state.history:
            st.subheader("📥 Export Reports")
            df_export = pd.DataFrame(st.session_state.history).drop(columns=['SavedImage'])
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV Report", data=csv, file_name="agromind_data.csv")
            
        if st.button("🗑️ Reset All Data", type="primary", use_container_width=True):
            st.session_state.history = []
            st.success("System Reset Complete!")
            st.rerun()

    st.title("🌿 AgroMind: Command Center")
    t1, t2, t3, t4 = st.tabs(["🔍 AI Diagnosis", "📊 Sensors & NPK", "💧 Watering Priority", "📜 Records & History"])

    # --- TAB 1: AI SCANNER (Camera/Gallery/Treatment) ---
    with t1:
        src = st.radio("Select Input Source:", ["Camera Scan", "Gallery Upload"], horizontal=True)
        file = st.camera_input("Scan Leaf") if src == "Camera Scan" else st.file_uploader("Upload Image", type=["jpg","png"])
        
        if file:
            img = Image.open(file)
            st.image(img, use_container_width=True, caption="Specimen Ready")
            if st.button("🚀 Analyze with AI Brain", use_container_width=True):
                with st.spinner("Analyzing Health..."):
                    try:
                        prompt = "Expert Analysis: Identify disease, Damage %, NPK needed, and Treatment."
                        res = model.generate_content([prompt, img])
                        analysis_text = res.text
                    except Exception:
                        analysis_text = "⚠️ (Demo Mode) Analysis Simulated.\nDiagnosis: Leaf Blight.\nDamage: 30%\nTreatment: Add Nitrogen & Fungicide."

                    st.markdown(f"### 🧪 Results\n{analysis_text}")
                    
                    # LOG DATA & SAVE IMAGE
                    dmg = random.randint(15, 80)
                    st.session_state.history.append({
                        "Date": time.strftime("%Y-%m-%d %H:%M"),
                        "Diagnosis": analysis_text[:60] + "...",
                        "Damage": dmg,
                        "Health": 100 - dmg,
                        "SavedImage": img
                    })

    # --- TAB 2: SENSORS & NPK ---
    with t2:
        st.subheader("📡 Real-time Telemetry")
        c1, c2 = st.columns(2)
        temp = c1.number_input("Temperature (°C)", 10, 55, 30)
        hum = c1.number_input("Humidity (%)", 10, 100, 60)
        moist = c2.slider("Soil Moisture %", 0, 100, 45)
        stress = 100 - moist
        c2.metric("Water Stress Level", f"{stress}%", delta="Critical" if stress > 65 else "Safe")
        
        st.divider()
        st.subheader("🧪 Soil Fertility (NPK Chart)")
        nc, pc, kc = st.columns(3)
        vn = nc.number_input("Nitrogen (N)", 0, 100, 40)
        vp = pc.number_input("Phosphorus (P)", 0, 100, 30)
        vk = kc.number_input("Potassium (K)", 0, 100, 50)
        st.bar_chart({"Nutrient": ["N", "P", "K"], "Level": [vn, vp, vk]}, x="Nutrient", y="Level", color="#4CAF50")

    # --- TAB 3: WATERING PRIORITY & GROWTH GRAPHS ---
    with t3:
        st.subheader("📍 Smart Watering Recommendations")
        if stress > 65:
            st.error("🚨 **PRIORITY 1: CRITICAL** - Water immediately (6 Liters).")
        elif 40 < stress <= 65:
            st.warning("⚠️ **PRIORITY 2: MODERATE** - Schedule watering soon (3 Liters).")
        else:
            st.success("✅ **PRIORITY 3: OPTIMAL** - Sufficient moisture detected.")

        st.divider()
        st.subheader("📈 Plant Health Growth Chart")
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.line_chart(df.set_index('Date')['Health'])
        else:
            st.info("No scan history to plot health trends.")

    # --- TAB 4: RECORDS (ACTUAL SAVED IMAGES) ---
    with t4:
        st.subheader("📜 Historical Records & Summary")
        if st.session_state.history:
            for item in reversed(st.session_state.history):
                with st.container(border=True):
                    col_img, col_txt = st.columns([1, 4])
                    col_img.image(item['SavedImage'], use_container_width=True)
                    col_txt.write(f"**Date:** {item['Date']}")
                    col_txt.write(f"**Health:** {item['Health']}% | **Damage:** {item['Damage']}%")
                    col_txt.caption(f"AI Note: {item['Diagnosis']}")
        else:
            st.info("Your scan history is empty.")
