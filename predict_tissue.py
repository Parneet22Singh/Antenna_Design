import joblib
import pandas as pd
import numpy as np

model = joblib.load("tissue_classifier.pkl")

eps0 = 8.854e-12

def predict_tissue(freq, eps, sigma):
    omega = 2 * np.pi * freq * 1e9
    penetration_depth = np.sqrt(2 / (omega * 4*np.pi*1e-7 * max(sigma, 1e-9)))
    loss_tangent = sigma / (omega * eps0 * eps)

    X = pd.DataFrame([{
        "Frequency": freq,
        "Permittivity": eps,
        "elec_cond": sigma,
        "penetration_depth": penetration_depth,
        "loss_tangent": loss_tangent
    }])

    return model.predict(X)[0]


# ---- Example tests ----
print(predict_tissue(2.4, 38.3, 1.35))  # Skin
print(predict_tissue(2.4, 10.8, 0.23))  # Fat
print(predict_tissue(2.4, 11.5, 0.34))  # Bone
print(predict_tissue(2.4, 1.0, 0.0))    # Air
