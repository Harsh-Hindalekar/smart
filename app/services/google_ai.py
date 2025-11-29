import httpx
from typing import List, Any

GOOGLE_API = "https://quickdraw-api.appspot.com/api/classify"

def format_for_google(points: List[Any]):
    stroke = []
    for p in points:
        if isinstance(p, str):
            x, y = p.split(",")
            stroke.append([float(x), float(y)])
        elif isinstance(p, (list, tuple)):
            stroke.append([float(p[0]), float(p[1])])
        elif isinstance(p, dict):
            stroke.append([float(p["x"]), float(p["y"])])
    return [stroke]   # Google expects list of strokes

async def recognize_google(points: List[Any]):
    payload = {"drawing": format_for_google(points)}
    async with httpx.AsyncClient() as client:
        res = await client.post(GOOGLE_API, json=payload)
        return res.json()
