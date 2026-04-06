import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import joblib

data = []
labels = []

dataset_path = "dataset"

# Check dataset exists
if not os.path.exists(dataset_path):
    print("Dataset folder not found!")
    exit()

for label in os.listdir(dataset_path):
    folder = os.path.join(dataset_path, label)

    # Skip if not folder
    if not os.path.isdir(folder):
        continue

    for img_name in os.listdir(folder):
        img_path = os.path.join(folder, img_name)

        img = cv2.imread(img_path)

        # Skip broken images
        if img is None:
            continue

        try:
            img = cv2.resize(img, (64, 64))
            img = img.flatten()

            data.append(img)
            labels.append(label)
        except:
            continue

# Convert to numpy
data = np.array(data)
labels = np.array(labels)

# Check if data loaded
if len(data) == 0:
    print("No images found! Check dataset folders.")
    exit()

# Split
X_train, X_test, y_train, y_test = train_test_split(
    data, labels, test_size=0.2, random_state=42
)

# Train model
model = SVC(kernel='linear')
model.fit(X_train, y_train)

# Accuracy
accuracy = model.score(X_test, y_test)
print("Model Accuracy:", accuracy)

# Save model
joblib.dump(model, "leaf_model.pkl")

print("Model saved successfully!")
