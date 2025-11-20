# model_loader.py
# COMPATIBILITY FIX FOR scikit-learn
import sklearn.compose._column_transformer

# Check if the required attribute exists, if not create it
if not hasattr(sklearn.compose._column_transformer, '_RemainderColsList'):
    class _RemainderColsList(list):
        pass


    sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList

# Now import other modules
import joblib
import json
import pandas as pd
import os
from django.conf import settings


class DiabetesModel:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.feature_names = None
        self.model_loaded = False
        self.load_models()

    def load_models(self):
        """Load model files from model_files directory in project root"""
        try:
            # The model_files directory is in the same directory as manage.py
            # BASE_DIR points to diabetes_diagnostic_system (where manage.py is)
            model_files_dir = os.path.join(settings.BASE_DIR, 'model_files')

            # Define file paths
            model_path = os.path.join(model_files_dir, 'optimized_random_forest_model.pkl')
            preprocessor_path = os.path.join(model_files_dir, 'preprocessor.pkl')
            features_path = os.path.join(model_files_dir, 'feature_names.json')

            # Check if files exist
            if not all(os.path.exists(path) for path in [model_path, preprocessor_path, features_path]):
                # If files not found, check what's available
                if os.path.exists(model_files_dir):
                    available_files = os.listdir(model_files_dir)
                    print(f"Available files in model_files directory: {available_files}")
                raise FileNotFoundError("Could not find all required model files in model_files directory")

            # Load the files
            self.model = joblib.load(model_path)
            self.preprocessor = joblib.load(preprocessor_path)

            with open(features_path, 'r') as f:
                self.feature_names = json.load(f)

            self.model_loaded = True
            print("✅ Model and preprocessor loaded successfully!")
            print(f"✅ Model file: {model_path}")
            print(f"✅ Preprocessor file: {preprocessor_path}")
            print(f"✅ Features file: {features_path}")

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("Please make sure the model files are in the model_files directory:")
            print(f"  - {os.path.join(settings.BASE_DIR, 'model_files')}")
            self.model_loaded = False

    def predict_diabetes(self, input_data):
        """Make prediction on new data"""
        if not self.model_loaded:
            return {'error': 'Model not loaded. Please check if model files exist.'}

        try:
            # Convert to DataFrame with correct column order
            input_df = pd.DataFrame([input_data])

            # Preprocess the input
            processed_data = self.preprocessor.transform(input_df)

            # Make prediction
            prediction = self.model.predict(processed_data)[0]
            probability = self.model.predict_proba(processed_data)[0]

            return {
                'diabetes_prediction': int(prediction),
                'probability_no_diabetes': float(probability[0]),
                'probability_diabetes': float(probability[1]),
                'confidence': float(max(probability)) * 100
            }

        except Exception as e:
            return {'error': str(e)}


# Global instance
diabetes_model = DiabetesModel()