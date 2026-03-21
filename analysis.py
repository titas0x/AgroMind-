import numpy as np
from PIL import Image

def analyze_leaf(image):
    # Convert image to RGB and then to a NumPy array
    img_array = np.array(image.convert('RGB'))
    
    # Calculate the average Red, Green, and Blue values
    avg_r = np.mean(img_array[:, :, 0])
    avg_g = np.mean(img_array[:, :, 1])
    avg_b = np.mean(img_array[:, :, 2])
    
    # Logic: Healthy leaves are Green. Dead/Dry leaves are Brown (Red + Green but low Blue).
    # If Green is significantly higher than Red, it's healthy.
    if avg_g > avg_r + 10:
        score = np.random.randint(80, 98) # Healthy range
    elif avg_r > avg_g:
        score = np.random.randint(30, 55) # Brown/Dry range
    else:
        score = np.random.randint(55, 79) # Yellowing/Stressed range
        
    return score

def get_soil_logic(moisture):
    if moisture < 35: 
        return "🔴 Dry", "CRITICAL: Irrigation required immediately."
    elif 35 <= moisture <= 75: 
        return "🟢 Optimal", "Condition is perfect for growth."
    else: 
        return "🔵 Over-watered", "WARNING: Reduce water to prevent root rot."

def get_nutrient_advice(score):
    if score < 60:
        return "Severe Stress", "Action: Immediate fertilization and hydration needed."
    elif score < 80: 
        return "Nitrogen (N) Deficiency", "Action: Apply organic compost or Urea fertilizer."
    return "Balanced", "Plant appears healthy and well-nourished."
