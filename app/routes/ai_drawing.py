from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

# ---------- Request Model ----------
class StrokeData(BaseModel):
    points: List[Dict[str, float]]

# ---------- AI Endpoint ----------
@router.post("/ai/perfect-drawing")
def perfect_drawing(data: StrokeData):
    points = data.points

    # For now we return same points (frontend AI handles shapes)
    return {
        "recognized_as": "shape",
        "confidence": 0.99,
        "smoothed_points": points
    }
# Note: The actual AI logic for recognizing and perfecting drawings
# is handled on the frontend side as per the current implementation.