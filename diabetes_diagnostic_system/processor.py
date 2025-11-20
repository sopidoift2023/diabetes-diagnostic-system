# recreate_preprocessor.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from imblearn.under_sampling import RandomUnderSampler
import joblib
import json

print("🔧 Recreating preprocessor with current scikit-learn version...")

# 1. Load and prepare your data
df = pd.read_csv("diabetes_prediction_dataset.csv")

# Drop HbA1c column as before
if "HbA1c_level" in df.columns:
    df = df.drop("HbA1c_level", axis=1)

# Basic cleaning
df = df.dropna()
df = df[(df['age'] > 0) & (df['age'] < 120)]
df = df[(df['bmi'] > 10) & (df['bmi'] < 60)]
df = df[(df['blood_glucose_level'] > 50) & (df['blood_glucose_level'] < 300)]

print("Dataset shape after cleaning:", df.shape)
print("Class distribution:")
print(df['diabetes'].value_counts())

# 2. Split data
X = df.drop('diabetes', axis=1)
y = df['diabetes']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set: {X_train.shape}")
print(f"Test set: {X_test.shape}")

# 3. Balance ONLY the training set
rus = RandomUnderSampler(random_state=42)
X_train_balanced, y_train_balanced = rus.fit_resample(X_train, y_train)

print("\nAfter balancing training set:")
print(pd.Series(y_train_balanced).value_counts())

# 4. Define preprocessing
numerical_features = ['age', 'bmi', 'blood_glucose_level', 'hypertension', 'heart_disease']
categorical_features = ['gender', 'smoking_history']

# Create preprocessor with current scikit-learn version
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features)
    ])

# 5. Fit preprocessor on training data only
preprocessor.fit(X_train_balanced)

# 6. Get feature names after preprocessing
cat_encoder = preprocessor.named_transformers_['cat']
cat_feature_names = cat_encoder.get_feature_names_out(categorical_features)
all_feature_names = numerical_features + list(cat_feature_names)

print(f"\nProcessed training set shape: {X_train_balanced.shape}")
print(f"Feature names: {all_feature_names}")

# 7. Save the new preprocessor
joblib.dump(preprocessor, 'model_files/preprocessor_new.pkl')

# Save feature names
with open('model_files/feature_names_new.json', 'w') as f:
    json.dump(all_feature_names, f)

print("\n✅ New preprocessor created and saved as 'preprocessor_new.pkl'")
print("✅ New feature names saved as 'feature_names_new.json'")

# 8. Test that the new preprocessor works
try:
    # Try loading the new preprocessor
    test_preprocessor = joblib.load('model_files/preprocessor_new.pkl')
    print("✅ New preprocessor loads successfully!")

    # Test with a small sample
    sample_data = X_train_balanced.head(1)
    transformed = test_preprocessor.transform(sample_data)
    print(f"✅ Preprocessor transforms data successfully! Shape: {transformed.shape}")

except Exception as e:
    print(f"❌ Error testing new preprocessor: {e}")