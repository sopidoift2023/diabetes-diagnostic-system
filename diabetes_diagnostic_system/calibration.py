# check_calibration.py
import joblib
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.metrics import brier_score_loss
import numpy as np

# Load your model, scaler, and TEST data (X_test, y_test)
model = joblib.load('random_forest_model.pkl')
scaler = joblib.load('scaler.pkl')
# X_test, y_test = ... (load your test set)

X_test_scaled = scaler.transform(X_test)

# Get the predicted probabilities for the positive class
prob_pos = model.predict_proba(X_test_scaled)[:, 1]

# 1. Calculate Brier Score (lower is better, 0 is perfect)
brier_score = brier_score_loss(y_test, prob_pos)
print(f"Brier Score: {brier_score:.4f}")

# 2. Create Calibration Curve
fraction_of_positives, mean_predicted_value = calibration_curve(y_test, prob_pos, n_bins=10, strategy='quantile')

# Plot the calibration curve
plt.figure(figsize=(10, 8))
plt.plot(mean_predicted_value, fraction_of_positives, "s-", label="Your Current Model")
plt.plot([0, 1], [0, 1], "k:", label="Perfectly Calibrated")

plt.xlabel('Mean Predicted Probability (Model Confidence)')
plt.ylabel('Fraction of Positives')
plt.title('Calibration Curve (Reliability Curve)')
plt.legend()
plt.grid(True)
plt.savefig('calibration_curve_before.png')
plt.show()

# Interpret the results
print("\nCalibration Diagnosis:")
if brier_score < 0.1:
    print("✅ Good calibration.")
elif brier_score < 0.2:
    print("⚠️  Moderate calibration. Improvement is possible.")
else:
    print("❌ Poor calibration. Strongly recommend recalibration.")