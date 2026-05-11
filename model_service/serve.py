from fastapi import FastAPI
import torch
import torch.nn as nn
import numpy as np
from pydantic import BaseModel

app = FastAPI()

IRIS_CLASSES = ["setosa", "versicolor", "virginica"]

class SimpleClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(4, 16)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(16, 3)

    def forward(self, x):
        return self.layer2(self.relu(self.layer1(x)))

model = None

@app.on_event("startup")
def load_model():
    global model
    model = SimpleClassifier()
    model.load_state_dict(torch.load("model/model.pth", map_location="cpu"))
    model.eval()

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}

class PredictionRequest(BaseModel):
    features: list[float]

@app.post("/predict")
def predict(req: PredictionRequest):
    x = torch.FloatTensor(req.features).unsqueeze(0)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)
        confidence, predicted = probs.max(dim=1)
    return {
        "prediction": IRIS_CLASSES[predicted.item()],
        "confidence": round(confidence.item(), 4),
        "model": "iris-classifier-v1"
    }