from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import pickle
import numpy as np
import pandas as pd
from itertools import product
import uvicorn
from xgboost import XGBClassifier
from catboost import CatBoostClassifier

app = FastAPI()
class PredictionRequest(BaseModel):
    sequence: str
    organism: str

def transform_sequence(sequence):
    """Compute kappa encoding for a given sequence."""
    length = len(sequence)
    total1 = 0
    for i in range(length - 1):
        sequence2 = sequence[i + 1:]
        length2 = len(sequence2)
        count1 = sum(1 for j in range(length2) if sequence[j] == sequence2[j])
        total1 += (count1 % length2) * 100
    total1 = (total1 / (length - 1)) * 100 if length > 1 else 0
    return total1

def transform_sequence_kmer(sequence):
    """Extract kappa encoded values for k-mers."""
    return [transform_sequence(sequence[i:i + 6]) for i in range(len(sequence) - 6 + 1)]

def preprocess_sequence(sequence):
    """Preprocess input sequence into numerical representation."""
    if len(sequence) != 150:
        raise ValueError("Sequence must be exactly 150 bases long.")
    
    sequence = sequence.upper()
    if any(base not in "ATGC" for base in sequence):
        raise ValueError("Invalid bases in sequence. Only A, T, G, C allowed.")
    
    transformed_seq = transform_sequence_kmer(sequence)
    expected_features = 150 - 6 + 1 
    if len(transformed_seq) != expected_features:
        raise ValueError(f"Invalid feature count. Expected {expected_features}, got {len(transformed_seq)}.")
    
    return np.array(transformed_seq).reshape(1, -1)

def load_models(organism):
    """Load all trained models for the given organism."""
    model_dir = f"models/{organism}"
    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"No models found for {organism}.")
    
    models = {}
    for filename in os.listdir(model_dir):
        model_path = os.path.join(model_dir, filename)
        model_name, ext = os.path.splitext(filename)
        
        try:
            if ext == ".pkl":
                with open(model_path, "rb") as f:
                    models[model_name] = pickle.load(f)
            elif ext == ".json":
                model = XGBClassifier()
                model.load_model(model_path)
                models[model_name] = model
            elif ext == ".cbm":
                model = CatBoostClassifier()
                model.load_model(model_path)
                models[model_name] = model
        except Exception as e:
            print(f"Error loading {model_name}: {str(e)}")
    
    if not models:
        raise RuntimeError("All models failed to load.")
    return models

@app.post("/predict")
def predict(request: PredictionRequest):
    """API endpoint to predict promoter sequences using multiple models."""
    try:
        processed_seq = preprocess_sequence(request.sequence)
        models = load_models(request.organism)

        predictions = {}
        for model_name, model in models.items():
            pred = model.predict(processed_seq)
            predictions[model_name] = int(pred[0]) 

        return {"organism": request.organism, "predictions": predictions}

    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fe:
        print(fe)
        raise HTTPException(status_code=404, detail=str(fe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
