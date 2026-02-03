import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load ITIS data
df = pd.read_csv("itis_full.csv") #or whatever name your file is saved with

# ---- Physics Features ----
mu0 = 4 * np.pi * 1e-7
eps0 = 8.854e-12

df["freq_hz"] = df["Frequency"] * 1e9
omega = 2 * np.pi * df["freq_hz"]

sigma = df["elec_cond"].replace(0, 1e-9)

df["penetration_depth"] = np.sqrt(2 / (omega * mu0 * sigma))
df["loss_tangent"] = df["elec_cond"] / (omega * eps0 * df["Permittivity"])

# ---- Tissue Classes ----
def classify(tissue):
    if "Fat" in tissue or "SAT" in tissue or "Breast Fat" in tissue:
        return "Fatty"
    elif "Bone" in tissue or "Tooth" in tissue or "Skull" in tissue:
        return "Hard"
    elif "Air" in tissue or "Lumen" in tissue:
        return "Air"
    else:
        return "HighWater"

df["TissueClass"] = df["Tissue"].apply(classify)

# ---- Train ML ----
X = df[[
    "Frequency",
    "Permittivity",
    "elec_cond",
    "penetration_depth",
    "loss_tangent"
]]

y = df["TissueClass"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=300)
model.fit(X_train, y_train)

joblib.dump(model, "tissue_classifier.pkl")
print("Model trained and saved.")
