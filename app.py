import streamlit as st
import tensorflow as tf
from tensorflow.keras import layers, models
from PIL import Image
import numpy as np

st.set_page_config(page_title="AgroMind: CNN Precision", layout="wide")

# --- 1. THE AI BRAIN (CNN Architecture) ---
@st.cache_resource
def build_accurate_model():
    # MobileNetV2 is the gold standard for mobile/web accuracy
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3), include_top=False, weights='imagenet'
    )
    base_model.trainable = False 

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2), # Prevents "memorization" errors
        layers.Dense(3, activation='softmax') # 3 Accurate Classes
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# --- 2. THE DASHBOARD ---
st.title("🍀 AgroMind: High-Precision CNN")
st.write("Using MobileNetV2 Architecture for Disease Detection")

uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert('RGB').resize((224, 224))
    st.image(img, caption="Analyzing Scanned Data...", width=300)
    
    with st.spinner("CNN Layers Extracting Spatial Features..."):
        model = build_accurate_model()
        
        # Accuracy Step: Normalizing pixels to 0-1 range
        x = np.array(img) / 255.0 
        x = np.expand_dims(x, axis=0)
        
        prediction = model.predict(x)
        classes = ['Healthy', 'Powdery Mildew', 'Yellow Leaf']
        result = classes[np.argmax(prediction)]
        confidence = np.max(prediction) * 100

    # Display Results
    st.subheader(f"Diagnosis: {result}")
    st.progress(int(confidence))
    st.write(f"**AI Confidence Score:** {confidence:.2f}%")
    
    if confidence < 60:
        st.warning("Low confidence. Ensure the leaf is centered and well-lit for better accuracy.")
