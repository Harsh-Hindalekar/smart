import math

# ---------------- UTILS ---------------- #

def distance(a, b):
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def centroid(points):
    cx = sum(p["x"] for p in points) / len(points)
    cy = sum(p["y"] for p in points) / len(points)
    return cx, cy


def bounding_box(points):
    xs = [p["x"] for p in points]
    ys = [p["y"] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------- SHAPE DETECTION ---------------- #

def detect_shape(points):
    if not points or len(points) < 6:
        return "unknown", 0.0

    min_x, min_y, max_x, max_y = bounding_box(points)
    width = max_x - min_x
    height = max_y - min_y

    cx, cy = centroid(points)

    # ---------------- CIRCLE (PRIORITY 1) ---------------- #

    radii = [distance(p, {"x": cx, "y": cy}) for p in points]
    avg_r = sum(radii) / len(radii)

    variance = sum((r - avg_r) ** 2 for r in radii) / len(radii)

    # path closure (start ≈ end)
    start_end_dist = distance(points[0], points[-1])

    if (
        variance < avg_r * 0.35
        and start_end_dist < avg_r * 0.6
        and 0.7 <= width / height <= 1.3
    ):
        confidence = min(0.98, 0.7 + (1 - variance / avg_r))
        return "circle", confidence

    # ---------------- TRIANGLE ---------------- #

    corners = 0
    for i in range(2, len(points) - 2):
        a = distance(points[i - 2], points[i])
        b = distance(points[i], points[i + 2])
        c = distance(points[i - 2], points[i + 2])

        if a * b == 0:
            continue

        angle = math.degrees(
            math.acos(max(-1, min(1, (a*a + b*b - c*c) / (2*a*b))))
        )

        if angle < 95:
            corners += 1

    if 2 <= corners <= 4:
        return "triangle", 0.9

    # ---------------- SQUARE / RECTANGLE ---------------- #

    if height != 0:
        ratio = width / height
        if 0.85 <= ratio <= 1.15:
            return "square", 0.92
        else:
            return "rectangle", 0.88
    # ---------------- LINE ---------------- #

    if len(points) >= 5:
        start = points[0]
        end = points[-1]
        max_dev = max(
            abs(
                (end["y"] - start["y"]) * p["x"]
                - (end["x"] - start["x"]) * p["y"]
                + end["x"] * start["y"]
                - end["y"] * start["x"]
                )
                / max(distance(start, end), 1)
                for p in points
                )
        if max_dev < 8:
            return "line", 0.95
        return "unknown", 0.4

# ---------------- PERFECT SHAPES ---------------- #

def smooth_points(shape, points):
    min_x, min_y, max_x, max_y = bounding_box(points)
    cx, cy = centroid(points)

    smoothed = []

    # ---- CIRCLE ----
    if shape == "circle":
        r = min(max_x - min_x, max_y - min_y) / 2
        for i in range(0, 360, 6):
            rad = math.radians(i)
            smoothed.append({
                "x": cx + r * math.cos(rad),
                "y": cy + r * math.sin(rad)
            })

    # ---- SQUARE ----
    elif shape == "square":
        size = min(max_x - min_x, max_y - min_y)
        smoothed = [
            {"x": min_x, "y": min_y},
            {"x": min_x + size, "y": min_y},
            {"x": min_x + size, "y": min_y + size},
            {"x": min_x, "y": min_y + size},
            {"x": min_x, "y": min_y},
        ]

    # ---- RECTANGLE ----
    elif shape == "rectangle":
        smoothed = [
            {"x": min_x, "y": min_y},
            {"x": max_x, "y": min_y},
            {"x": max_x, "y": max_y},
            {"x": min_x, "y": max_y},
            {"x": min_x, "y": min_y},
        ]

    # ---- TRIANGLE ----
    elif shape == "triangle":
        smoothed = [
            {"x": cx, "y": min_y},
            {"x": min_x, "y": max_y},
            {"x": max_x, "y": max_y},
            {"x": cx, "y": min_y},
        ]
                
    else:
        return points

    return smoothed
