from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Stroke(BaseModel):
    points: list

@router.post("/ai/perfect-drawing")
def perfect_drawing(data: Stroke):
    return {
        "recognized_as": "circle",
        "confidence": 0.9,
        "smoothed_points": data.points
    }
