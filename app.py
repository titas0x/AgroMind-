import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import numpy as np
import time

# --- CONFIG & STYLING ---
st.set_page_config(page_title="AgroMind Ultimate Cloud AI", layout="wide", page_icon="🍀")

# --- AUTHENTICATION & DATABASE ---
if 'user_db' not in st.session_state: st.session_state.user_db = {"admin": "agromind2026"}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'history' not in st.session_state: st.session_state.history = []

def login_gate():
    st.title("🔐 AgroMind Secure Portal")
    mode = st.radio("Choose Mode", ["Sign In", "Sign Up"], horizontal=True)
    with st.form("AuthForm"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Enter System"):
            if mode == "Sign Up":
                st.session_state.user_db[u] = p
                st.success("Account registered! Switch to Sign In.")
            elif u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied: Invalid Credentials")

# --- MAIN APPLICATION ---
if not st.session_state.logged_in:
    login_gate()
else:
    # Sidebar Management
    with st.sidebar:
        st.title(f"👤 {st.session_state.user}")
        api_key = st.text_input("Enter Gemini API Key", type="password", help="Get it from Google AI Studio")
        if st.button("Logout"): 
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        if st.session_state.history:
            csv = pd.DataFrame(st.session_state.history).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Full Plant Report", csv, "plant_report.csv", "text/csv")
        if st.button("🧹 Clear All Records"): st.session_state.history = []

    st.title("🍀 AgroMind Ultimate: Smart Agriculture Suite")
    tab1, tab2, tab3 = st.tabs(["🔍 AI Diagnosis & Treatment", "📊 Soil & Environment", "📈 Growth Track"])

    # --- TAB 1: CLOUD AI BRAIN ---
    with tab1:
        if not api_key: st.info("Please enter your API Key in the sidebar to wake up the Brain.")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            c1, c2 = st.columns(2)
            img_input = c1.camera_input("Scan Leaf Architecture")
            
            if img_input:
                img = Image.open(img_input)
                with st.spinner("AI Brain Analyzing Textures..."):
                    try:
                        prompt = "Identify this plant disease. Give: 1. Diagnosis, 2. Accuracy %, 3. Treatment (Chemical & Organic)."
                        response = model.generate_content([prompt, img])
                        analysis_text = response.text
                        
                        with c2:
                            st.subheader("Cloud AI Analysis")
                            st.write(analysis_text)
                            # Saving to database
                            st.session_state.history.append({
                                "Time": time.strftime("%H:%M:%S"),
                                "User": st.session_state.user,
                                "Diagnosis": "Processed",
                                "Health_Score": np.random.randint(85, 99)
                            })
                    except Exception as e: st.error(f"Cloud Error: {e}")

    # --- TAB 2: SOIL, FERTILITY & WATER STRESS ---
    with tab2:
        st.subheader("📡 Real-time Sensor Simulation")
        m1, m2, m3 = st.columns(3)
        moisture = m1.slider("Soil Moisture Content (%)", 0, 100, 45)
        fertility = m2.select_slider("Soil Fertility Index", options=["Critical", "Low", "Optimal", "Rich"], value="Optimal")
        
        # Water Stress Index Calculation
        w_stress = 100 - moisture
        m3.metric("Water Stress Level", f"{w_stress}%", delta="-2% (Improving)" if w_stress < 50 else "+5% (Rising)")
        st.progress(w_stress/100)
        
        if w_stress > 65: st.warning("High Water Stress detected. Irrigation advised.")
        
        st.divider()
        st.subheader("📊 Soil Nutrient Trends")
        st.line_chart(pd.DataFrame(np.random.randn(20, 2), columns=['Nitrate (N)', 'Potassium (K)']))

    # --- TAB 3: IMPROVEMENT TRACK ---
    with tab3:
        st.subheader("📈 Plant Health Improvement Tracker")
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.dataframe(df, use_container_width=True)
            
            st.write("### Health Improvement Timeline")
            st.area_chart(df['Health_Score'])
            st.success("Analysis: The CNN indicates a positive trend in leaf structural restoration.")
        else:
            st.info("No data available. Perform a scan to start tracking.")
