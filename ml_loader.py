"""
ml_loader.py - Machine Learning model loader for Agri Smart
Loads models once at startup and stores them on the Flask app object.
"""

import os
import pickle
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Tomato disease class labels (must match training order)
TOMATO_CLASSES = [
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

# User-friendly display names
TOMATO_DISEASE_DISPLAY = {
    "Tomato___Bacterial_spot": "Bacterial Spot",
    "Tomato___Early_blight": "Early Blight",
    "Tomato___Late_blight": "Late Blight",
    "Tomato___Leaf_Mold": "Leaf Mold",
    "Tomato___Septoria_leaf_spot": "Septoria Leaf Spot",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Spider Mites",
    "Tomato___Target_Spot": "Target Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Yellow Leaf Curl Virus",
    "Tomato___Tomato_mosaic_virus": "Tomato Mosaic Virus",
    "Tomato___healthy": "Healthy Leaf",
}

# Crop label mapping (1-indexed, matching training)
CROP_MAPPING = {
    1: "rice", 2: "maize", 3: "chickpea", 4: "kidneybeans",
    5: "pigeonpeas", 6: "mothbeans", 7: "mungbean", 8: "blackgram",
    9: "lentil", 10: "pomegranate", 11: "banana", 12: "mango",
    13: "grapes", 14: "watermelon", 15: "muskmelon", 16: "apple",
    17: "orange", 18: "papaya", 19: "coconut", 20: "cotton",
    21: "jute", 22: "coffee",
}


def load_models(app):
    """
    Load all ML models at Flask startup.
    Stores references as app-level attributes so they are reused
    across all requests without reloading.
    """
    models_dir = app.config.get('ML_MODELS_FOLDER', 'ml_models')

    # -----------------------------------------------------------------------
    # Load Crop Recommendation (Random Forest + MinMaxScaler)
    # -----------------------------------------------------------------------
    crop_model_path  = os.path.join(models_dir, 'model.pkl')
    crop_scaler_path = os.path.join(models_dir, 'minmaxscaler.pkl')

    app.crop_model  = None
    app.crop_scaler = None

    try:
        with open(crop_model_path, 'rb') as f:
            app.crop_model = pickle.load(f)
        logger.info("✅ Crop Recommendation model loaded successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to load crop model: {e}")

    try:
        with open(crop_scaler_path, 'rb') as f:
            app.crop_scaler = pickle.load(f)
        logger.info("✅ Crop scaler loaded successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to load crop scaler: {e}")

    # -----------------------------------------------------------------------
    # Load Tomato Disease (EfficientNetB3 TFLite model)
    # -----------------------------------------------------------------------
    tomato_model_path = os.path.join(models_dir, 'tomato_model.tflite')

    app.tomato_interpreter = None

    try:
        try:
            from ai_edge_litert.interpreter import Interpreter
        except ImportError:
            try:
                from tflite_runtime.interpreter import Interpreter
            except ImportError:
                from tensorflow.lite.python.interpreter import Interpreter

        interpreter = Interpreter(model_path=tomato_model_path)
        interpreter.allocate_tensors()
        app.tomato_interpreter = interpreter
        logger.info("Tomato Disease TFLite model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load tomato TFLite model: {e}")
