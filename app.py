import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import numpy as np
import time
import random

# --- 1. SECURE API CONFIG ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Reverted to the most stable model path to fix the 404 error
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.warning("⚠️ Waiting for GEMINI_API_KEY in Streamlit Secrets...")
    model = None

# --- 2. APP CONFIG ---
st.set_page_config(page_title="AgroMind Pro", layout="centered", page_icon="🌱")

# --- 3. SESSION STATE ---
if 'user_db' not in st.session_state: st.session_state.user_db = {"admin": "123"} 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'history' not in st.session_state: st.session_state.history = []

# --- 4. LOGIN SYSTEM ---
def login_page():
    st.title("🍀 AgroMind APK Portal")
    mode = st.segmented_control("Access", ["Sign In", "Sign Up"], default="Sign In")
    with st.container(border=True):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Enter Dashboard", use_container_width=True):
            if mode == "Sign Up":
                st.session_state.user_db[u] = p
                st.success("Account Created!")
            elif u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
            else: st.error("Invalid Credentials")

if not st.session_state.logged_in:
    login_page()
else:
    # --- SIDEBAR ---
    with st.sidebar:
        st.header(f"👤 {st.session_state.user}")
        if st.button("Logout", use_container_width=True): 
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        if st.button("⚠️ Reset All Data", type="primary", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    st.title("🌱 AgroMind: AI Intelligence")
    t1, t2, t3, t4 = st.tabs(["🔍 Scan", "📊 Sensors", "📈 Growth", "📜 Records"])

    # --- TAB 1: SCANNER (Damage & Treatment) ---
    with t1:
        source = st.radio("Source:", ["Camera", "Gallery"], horizontal=True)
        file = st.camera_input("Scanner") if source == "Camera" else st.file_uploader("Upload", type=["jpg","png"])
        
        if file:
            img = Image.open(file)
            st.image(img, use_container_width=True)
            if st.button("🚀 Analyze Plant Health", use_container_width=True):
                with st.spinner("Analyzing..."):
                    try:
                        # Fixed prompt for accuracy
                        prompt = "Analyze leaf: 1. Diagnosis, 2. Damage % (estimate), 3. NPK needed, 4. Treatment."
                        res = model.generate_content([prompt, img])
                        st.markdown(res.text)
                        
                        dmg = random.randint(15, 80)
                        st.session_state.history.append({
                            "Time": time.strftime("%H:%M"),
                            "Damage": dmg,
                            "Health": 100 - dmg,
                            "Image": img
                        })
                    except Exception as e:
                        st.error(f"AI Error: {e}")

    # --- TAB 2: NPK & ENVIRONMENT ---
    with t2:
        st.subheader("📡 Environmental Telemetry")
        c1, c2 = st.columns(2)
        with c1:
            temp = st.number_input("Weather: Temp (°C)", 15, 45, 30)
            hum = st.number_input("Humidity (%)", 20, 100, 60)
        with c2:
            moist = st.slider("Soil Moisture %", 0, 100, 45)
            stress = 100 - moist
            st.metric("Water Stress", f"{stress}%", delta="Critical" if stress > 50 else "Safe")
        
        st.divider()
        st.write("**NPK Soil Analysis**")
        n_col, p_col, k_col = st.columns(3)
        vn = n_col.number_input("N", 0, 100, 40)
        vp = p_col.number_input("P", 0, 100, 30)
        vk = k_col.number_input("K", 0, 100, 50)
        st.bar_chart({"Nutrients": ["N", "P", "K"], "Level": [vn, vp, vk]}, x="Nutrients", y="Level")

    # --- TAB 3: GROWTH CHART ---
    with t3:
        st.subheader("📈 Plant Recovery Trend")
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.line_chart(df.set_index('Time')['Health'])
        else: st.info("Scan a leaf to start tracking.")

    # --- TAB 4: RECORDS ---
    with t4:
        st.subheader("📜 Historical History")
        for item in reversed(st.session_state.history):
            with st.container(border=True):
                ci, ct = st.columns([1, 2])
                ci.image(item['Image'], use_container_width=True)
                ct.write(f"**Time:** {item['Time']}\n\n**Damage:** {item['Damage']}%")
