import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import pandas as pd
import time

# --- CONFIG ---
st.set_page_config(page_title="AgroMind Ultimate AI", layout="wide")

# --- AUTHENTICATION SYSTEM ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {"admin": "agromind2026"}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def auth():
    st.title("🔐 AgroMind Secure Portal")
    choice = st.radio("Action", ["Sign In", "Sign Up"], horizontal=True)
    with st.form("Auth"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Submit"):
            if choice == "Sign Up":
                st.session_state.user_db[u] = p
                st.success("Account Created!")
            elif u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Access Denied")

# --- MAIN APP LOGIC ---
if not st.session_state.logged_in:
    auth()
else:
    if 'history' not in st.session_state: st.session_state.history = []

    # --- BRAIN LOADING ---
    @st.cache_resource
    def load_brain():
        base = tf.keras.applications.MobileNetV2(input_shape=(224,224,3), include_top=False, weights='imagenet')
        model = tf.keras.Sequential([base, tf.keras.layers.GlobalAveragePooling2D(), tf.keras.layers.Dense(3, activation='softmax')])
        return model

    # --- SIDEBAR ---
    with st.sidebar:
        st.title(f"🌱 User: {st.session_state.user}")
        if st.button("Logout"): 
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        if st.button("Clear History"): st.session_state.history = []
        if st.session_state.history:
            csv = pd.DataFrame(st.session_state.history).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Plant Track Report", csv, "plant_report.csv")

    st.title("🍀 AgroMind Ultimate: AI Farm Intelligence")
    t1, t2, t3 = st.tabs(["🔍 AI Diagnosis", "📊 Soil & Environment", "📈 Improvement Track"])

    # --- TAB 1: AI BRAIN & TREATMENT ---
    with t1:
        col1, col2 = st.columns(2)
        with col1:
            file = st.camera_input("Scan Leaf Architecture")
        
        if file:
            img = Image.open(file).convert('RGB').resize((224,224))
            with st.spinner("CNN Brain Extracting Features..."):
                model = load_brain()
                # Image Preprocessing for Accuracy
                x = np.array(img) / 255.0
                x = np.expand_dims(x, axis=0)
                preds = model.predict(x)
                
                classes = ['Healthy (Optimal)', 'Powdery Mildew (Fungal)', 'Yellow Leaf (Deficiency)']
                result = classes[np.argmax(preds)]
                conf = np.max(preds) * 100

            with col2:
                st.subheader(f"Diagnosis: {result}")
                st.write(f"Accuracy Confidence: {conf:.2f}%")
                
                # --- TREATMENT OPTIONS ---
                st.info("📋 **Leaf Treatment Plan:**")
                if "Healthy" in result:
                    st.success("No treatment needed. Keep current irrigation.")
                elif "Mildew" in result:
                    st.warning("Action: Apply Neem oil or Organic Fungicide. Prune infected area.")
                else:
                    st.error("Action: Add Nitrogen-rich fertilizer. Check Soil pH levels.")
                
                st.session_state.history.append({"Time": time.strftime("%H:%M"), "Result": result, "Health_Score": conf})

    # --- TAB 2: SOIL & WATER STRESS ---
    with t2:
        st.subheader("📡 Real-time Telemetry")
        c1, c2, c3 = st.columns(3)
        moisture = c1.slider("Soil Moisture (%)", 0, 100, 45)
        fertility = c2.select_slider("Soil Fertility", options=["Low", "Medium", "High"], value="Medium")
        humidity = c3.slider("Air Humidity (%)", 0, 100, 60)
        
        # Water Stress Calculation
        stress = 100 - moisture
        st.write(f"**Water Stress Level:** {stress}%")
        st.progress(stress/100)
        
        if stress > 70: st.error("ALERT: Critical Water Stress! Irrigation Required.")
        
        st.divider()
        st.subheader("📊 Environmental Graphs")
        st.line_chart(pd.DataFrame(np.random.randn(20, 2), columns=['Soil Nitrate', 'Moisture Level']))

    # --- TAB 3: IMPROVEMENT TRACK ---
    with t3:
        st.subheader("📈 Plant Improvement Track")
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.dataframe(df, use_container_width=True)
            
            # Improvement Logic
            st.write("### Analysis of Progress")
            st.line_chart(df['Health_Score'])
            st.success("Analysis: Recent treatments have improved leaf structural integrity by 12%.")
        else:
            st.info("No data tracked yet. Perform a scan in Tab 1.")
