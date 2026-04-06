import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import datetime
import cv2
import joblib
import os
import importlib.util

st.set_page_config(page_title="AgroMind", layout="wide")

# ----------------- AUTO MODEL HANDLING (FIXED) -----------------

MODEL_PATH = os.path.join(os.path.dirname(__file__), "leaf_model.pkl")

model = None

def train_model_auto():
    """
    Automatically runs train_model.py if model doesn't exist.
    """
    try:
        st.info("Training model automatically...")

        spec = importlib.util.spec_from_file_location(
            "train_model", os.path.join(os.path.dirname(__file__), "train_model.py")
        )
        train_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(train_module)

        st.success("Training completed")

    except Exception as e:
        st.error(f"Auto training failed: {e}")

# Try loading model
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        st.sidebar.success("AI Model Loaded")
    except Exception as e:
        st.sidebar.error(f"Model load failed: {e}")
        model = None
else:
    train_model_auto()

    # try loading again after training
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            st.sidebar.success("AI Model Loaded after training")
        except Exception as e:
            st.sidebar.error(f"Model still failed: {e}")
            model = None
    else:
        st.sidebar.error("Model could not be created")

# ----------------- SESSION STATE -----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "water_logs" not in st.session_state:
    st.session_state.water_logs = []

# ----------------- PREPROCESS -----------------
def preprocess(img):
    img = img.resize((256,256))
    img_array = np.array(img)

    blur = cv2.GaussianBlur(img_array,(5,5),0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    return img_array, hsv, gray

# ----------------- ANALYZE -----------------
def analyze_leaf(img, dryness):
    img_array, hsv, gray = preprocess(img)

    # AI Prediction
    if model:
        try:
            img_resized = cv2.resize(img_array, (64,64))
            img_flat = img_resized.flatten().reshape(1, -1)
            prediction = model.predict(img_flat)[0]
        except:
            prediction = "Unknown"
    else:
        prediction = "Model not loaded"

    green = cv2.inRange(hsv, (30,40,40), (90,255,255))
    yellow = cv2.inRange(hsv, (15,50,50), (35,255,255))
    brown = cv2.inRange(hsv, (5,50,50), (20,255,200))

    edges = cv2.Canny(gray, 50, 150)
    pest_mask = edges

    total = 256*256

    green_ratio = np.sum(green > 0) / total
    yellow_ratio = np.sum(yellow > 0) / total
    brown_ratio = np.sum(brown > 0) / total
    pest_ratio = np.sum(pest_mask > 0) / total

    health = (
        green_ratio*100
        - brown_ratio*150
        - pest_ratio*120
        - yellow_ratio*80
        - dryness*0.15
    )

    health = max(5, min(100, health))
    damage = 100 - health

    if prediction == "healthy":
        health = max(85, health)

    return {
        "health": health,
        "damage": damage,
        "pest_ratio": pest_ratio,
        "green_mask": green,
        "yellow_mask": yellow,
        "brown_mask": brown,
        "pest_mask": pest_mask,
        "yellow_ratio": yellow_ratio,
        "brown_ratio": brown_ratio,
        "ai_prediction": prediction
    }

# ----------------- DISEASE DETECTION -----------------
def detect_disease(res, dryness):

    diseases = []
    solutions = []
    meds = []

    pred = res.get("ai_prediction")

    if pred == "fungal":
        diseases.append("Fungal Infection")
        solutions.append("Apply antifungal spray")
        meds.append(["Carbendazim","Mancozeb"])

    elif pred == "pest":
        diseases.append("Pest Attack")
        solutions.append("Use neem oil")
        meds.append(["Neem Oil"])

    elif pred == "nutrient":
        diseases.append("Nutrient Deficiency")
        solutions.append("Add fertilizers")
        meds.append(["NPK"])

    if res["brown_ratio"] > 0.15:
        diseases.append("Fungal Infection")
        solutions.append("Apply antifungal spray")
        meds.append(["Carbendazim"])

    if res["pest_ratio"] > 0.05:
        diseases.append("Pest Attack")
        solutions.append("Use neem oil")
        meds.append(["Neem Oil"])

    if dryness > 60:
        diseases.append("Water Stress")
        solutions.append("Increase watering")
        meds.append(["Irrigation"])

    if not diseases:
        diseases = ["Healthy Leaf"]
        solutions = ["No action needed"]
        meds = [["None"]]

    return diseases, solutions, meds

# ----------------- MULTI VIEW -----------------
def multi_view(images, dryness):
    results = []

    H, D, P = [], [], []

    for img in images:
        res = analyze_leaf(img, dryness)
        results.append(res)

        H.append(res["health"])
        D.append(res["damage"])
        P.append(res["pest_ratio"])

    return results, np.mean(H), np.mean(D), np.mean(P)

# ----------------- SOIL -----------------
def soil_analysis(h,dryness):
    moisture = max(10,70 - dryness/2 - (100-h)/2)
    water_stress = "High" if moisture<25 else "Low"
    fertility = "High" if h>75 else "Moderate"
    N = max(10,100-h)
    P = max(5,80-h)
    K = max(5,60-h)
    return moisture, water_stress, fertility, N, P, K

# ----------------- UI -----------------
st.title("🌱 AgroMind System")

menu = st.sidebar.radio("Menu",["Analysis","Batch Summary","Water Tracker","Guide","Instructions"])
dryness = st.sidebar.slider("Dryness",0,100,10)

# ----------------- ANALYSIS -----------------
if menu == "Analysis":

    mode = st.radio("Input",["Camera","Upload"])
    images = []

    if mode == "Camera":
        cam = st.camera_input("Capture")
        if cam:
            images.append(Image.open(cam))
    else:
        files = st.file_uploader("Upload",accept_multiple_files=True)
        if files:
            images = [Image.open(f) for f in files]

    if images:

        results, h,d,p = multi_view(images,dryness)

        st.subheader("Results")

        for i,res in enumerate(results):

            diseases, sol, meds = detect_disease(res,dryness)

            st.write("Health:", round(res["health"],2))
            st.write("AI:", res["ai_prediction"])

            st.image(images[i])

            for j in range(len(diseases)):
                st.warning(diseases[j])
                st.write(sol[j])

        m,w,f,N,P,K = soil_analysis(h,dryness)

        st.subheader("Soil")
        st.write(m,w,f)
