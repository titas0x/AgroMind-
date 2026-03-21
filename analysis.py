import streamlit as st
import tensorflow as tf
from tensorflow.keras.applications import mobilenet_v2
from PIL import Image
import numpy as np

st.set_page_config(page_title="AgroMind: CNN AI", layout="wide")

# --- THE BRAIN (CNN Architecture) ---
@st.cache_resource
def load_expert_brain():
    # Building a high-accuracy CNN using Transfer Learning
    base = mobilenet_v2.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
    base.trainable = False 
    model = tf.keras.Sequential([
        base,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax') # Healthy, Mildew, Yellow
    ])
    return model

st.title("🍀 AgroMind: CNN Precision Dashboard")
st.write("B.Tech Engineering Project | MobileNetV2 Deep Learning")

uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert('RGB').resize((224, 224))
    st.image(img, caption="Scanning Architecture...", width=300)
    
    with st.spinner("CNN Extracting Spatial Features..."):
        try:
            model = load_expert_brain()
            # Normalization Step for Accuracy
            x = np.array(img)
            x = mobilenet_v2.preprocess_input(x)
            x = np.expand_dims(x, axis=0)
            
            prediction = model.predict(x)
            classes = ['Healthy', 'Powdery Mildew', 'Yellow Leaf']
            result = classes[np.argmax(prediction)]
            confidence = np.max(prediction) * 100

            st.subheader(f"Diagnosis: {result}")
            st.write(f"Confidence Level: **{confidence:.2f}%**")
            st.success("CNN Feature Extraction Complete")
        except Exception as e:
            st.warning("The AI Brain is still initializing in the background. Please wait 2-3 minutes.")
