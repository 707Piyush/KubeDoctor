
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest


# Step 1: Create sample normal memory usage data
np.random.seed(42)

normal_memory = np.random.normal(
    loc=130,
    scale=20,
    size=200
)

# Keep memory values within a realistic demo range
normal_memory = np.clip(normal_memory, 80, 180)

# Step 2: Create a DataFrame
data = pd.DataFrame({
    "memory_usage": normal_memory
})

# Step 3: Train Isolation Forest
model = IsolationForest(
    contamination=0.05,
    random_state=42
)

model.fit(data[["memory_usage"]])

# Step 4: Save the training data
data.to_csv("ml/training_data.csv", index=False)

# Step 5: Save the trained model
joblib.dump(model, "ml/memory_model.pkl")

print("================================")
print("KUBEDOCTOR ML MODEL TRAINED")
print("================================")

print("Training samples:", len(data))
print("Average normal memory:", round(data["memory_usage"].mean(), 2), "MiB")

print("\nTraining data saved: ml/training_data.csv")
print("Model saved: ml/memory_model.pkl")
