from typing import List, Any, Optional, Dict
import httpx
import math
import json

GOOGLE_API = "https://quickdraw-api.appspot.com/api/classify"

def normalize_points(points: List[Any], canvas_width: float = 800, canvas_height: float = 500) -> List[Dict]:
    """Normalize canvas pixel coordinates to 0-255 range for QuickDraw API."""
    if not points:
        return []
    
    try:
        normalized = []
        for p in points:
            if isinstance(p, dict):
                x = float(p.get("x", 0))
                y = float(p.get("y", 0))
            else:
                x = float(p[0]) if len(p) > 0 else 0
                y = float(p[1]) if len(p) > 1 else 0
            
            norm_x = (x / canvas_width) * 255 if canvas_width > 0 else x
            norm_y = (y / canvas_height) * 255 if canvas_height > 0 else y
            normalized.append({"x": norm_x, "y": norm_y})
        
        print(f"✓ Normalized {len(normalized)} points")
        return normalized
    except Exception as e:
        print(f"✗ Error normalizing points: {e}")
        return []

def format_for_google(points: List[Any]) -> List[List[List[float]]]:
    """Format normalized points for QuickDraw classify API."""
    try:
        if not points:
            return [[]]
        
        normalized = normalize_points(points)
        if not normalized:
            return [[]]
        
        stroke = [[p['x'], p['y']] for p in normalized]
        print(f"✓ Formatted stroke with {len(stroke)} points")
        return [stroke]
    except Exception as e:
        print(f"✗ Error formatting points: {e}")
        return [[]]

async def recognize_google(points: List[Any]) -> dict:
    """Call QuickDraw classify API and return JSON result."""
    try:
        payload = {"drawing": format_for_google(points)}
        print(f"→ Sending request to QuickDraw API...")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(GOOGLE_API, json=payload)
            resp.raise_for_status()
            result = resp.json()
            print(f"✓ QuickDraw response received: {list(result.keys())}")
            return result
    except httpx.HTTPError as e:
        print(f"✗ HTTP Error: {e}")
        return {"error": f"HTTP Error: {str(e)}", "recognized": []}
    except Exception as e:
        print(f"✗ Error calling QuickDraw: {e}")
        return {"error": str(e), "recognized": []}

def get_top_prediction(recognition_result: dict) -> Optional[Dict]:
    """Return top prediction dict or None."""
    try:
        preds = recognition_result.get("recognized") or recognition_result.get("predictions") or []
        if isinstance(preds, list) and len(preds) > 0:
            print(f"✓ Found prediction: {preds[0]}")
            return preds[0]
        print(f"✗ No predictions in response")
        return None
    except Exception as e:
        print(f"✗ Error getting prediction: {e}")
        return None

def smooth_points(points: List[Dict], window: int = 3) -> List[Dict]:
    """Smooth points using moving average."""
    try:
        if len(points) < 3:
            return points[:]
        
        smoothed = []
        n = len(points)
        for i in range(n):
            sx = 0.0
            sy = 0.0
            count = 0
            for j in range(max(0, i - window), min(n, i + window + 1)):
                sx += points[j].get('x', 0)
                sy += points[j].get('y', 0)
                count += 1
            if count > 0:
                smoothed.append({'x': sx / count, 'y': sy / count})
        
        print(f"✓ Smoothed {len(points)} → {len(smoothed)} points")
        return smoothed
    except Exception as e:
        print(f"✗ Error smoothing: {e}")
        return points[:]

def perpendicular_distance(pt: Dict, line_start: Dict, line_end: Dict) -> float:
    """Calculate perpendicular distance for RDP simplification."""
    try:
        x0 = pt.get('x', 0)
        y0 = pt.get('y', 0)
        x1 = line_start.get('x', 0)
        y1 = line_start.get('y', 0)
        x2 = line_end.get('x', 0)
        y2 = line_end.get('y', 0)
        
        if x1 == x2 and y1 == y2:
            return math.hypot(x0 - x1, y0 - y1)
        
        num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        den = math.hypot(y2 - y1, x2 - x1)
        return num / den if den != 0 else 0
    except Exception as e:
        print(f"✗ Error calculating distance: {e}")
        return 0

def rdp(points: List[Dict], epsilon: float = 2.0) -> List[Dict]:
    """Ramer–Douglas–Peucker simplification algorithm."""
    try:
        if len(points) < 3:
            return points[:]
        
        dmax = 0.0
        index = 0
        for i in range(1, len(points) - 1):
            d = perpendicular_distance(points[i], points[0], points[-1])
            if d > dmax:
                index = i
                dmax = d
        
        if dmax > epsilon:
            rec1 = rdp(points[:index + 1], epsilon)
            rec2 = rdp(points[index:], epsilon)
            return rec1[:-1] + rec2
        else:
            return [points[0], points[-1]]
    except Exception as e:
        print(f"✗ Error in RDP: {e}")
        return points[:]

async def perfect_drawing(points: List[Any], smoothing_window: int = 3, simplify_eps: float = 2.0) -> dict:
    """
    Recognize the drawing and return perfected version.
    """
    try:
        print(f"\n--- perfect_drawing called ---")
        print(f"Received {len(points) if points else 0} points")
        
        original = []
        for p in points:
            try:
                if isinstance(p, dict):
                    original.append({'x': float(p.get('x', 0)), 'y': float(p.get('y', 0))})
                else:
                    original.append({'x': float(p[0]), 'y': float(p[1])})
            except (IndexError, TypeError, ValueError) as e:
                print(f"✗ Error parsing point {p}: {e}")
                continue
        
        if not original:
            return {
                "original_points": [],
                "smoothed_points": [],
                "recognized_as": None,
                "confidence": 0.0,
                "all_predictions": [],
                "error": "No valid points provided"
            }
        
        print(f"✓ Converted to {len(original)} points")
        
        # Recognize
        rec = await recognize_google(points)
        top = get_top_prediction(rec)
        name = top.get("name") if top else None
        confidence = float(top.get("score", 0.0)) if top else 0.0
        
        # Smooth and simplify
        smoothed = smooth_points(original, window=smoothing_window)
        simplified = rdp(smoothed, epsilon=simplify_eps)
        
        print(f"✓ Final: {len(simplified)} simplified points")
        print(f"--- perfect_drawing complete ---\n")
        
        return {
            "original_points": original,
            "smoothed_points": simplified,
            "recognized_as": name,
            "confidence": confidence,
            "all_predictions": rec.get("recognized") or rec.get("predictions") or [],
            "error": rec.get("error")
        }
    except Exception as e:
        print(f"✗ FATAL ERROR in perfect_drawing: {e}")
        import traceback
        traceback.print_exc()
        return {
            "original_points": [],
            "smoothed_points": [],
            "recognized_as": None,
            "confidence": 0.0,
            "all_predictions": [],
            "error": f"Server error: {str(e)}"
        }   ,          