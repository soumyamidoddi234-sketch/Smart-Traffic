import os
import tempfile
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from controller import plan

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024
CORS(app)


def _clean(vals, default=None):
    if vals is None:
        return default
    if not isinstance(vals, list) or len(vals) != 4:
        raise ValueError("Expected a list of 4 numbers")
    return [max(0.0, float(v)) for v in vals]


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(ok=True)


@app.post("/plan")
def plan_route():
    """Counts in -> signal plan out. Tiny payload, works on any host."""
    try:
        data = request.get_json(force=True)
        counts = _clean(data.get("counts"))
        prev = _clean(data.get("prev"), counts)
        lane = data.get("emergency_lane")
        lane = int(lane) if lane not in (None, "", -1) else None
        if lane is not None and not 0 <= lane <= 3:
            raise ValueError("emergency_lane must be 0-3")
        return jsonify(plan(counts, prev, lane))
    except (ValueError, TypeError) as e:
        return jsonify(error=str(e)), 400


@app.post("/analyze")
def analyze():
    """4 videos in -> counts + plan out. Needs a host that allows large uploads."""
    from counter import count_vehicles   # lazy import keeps the app booting if cv2 is missing
    files = [request.files.get(f"video{i}") for i in range(4)]
    if not all(files):
        return jsonify(error="Upload 4 videos: video0 to video3"), 400
    counts = []
    for f in files:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as t:
            f.save(t.name)
        try:
            counts.append(count_vehicles(t.name))
        except Exception as e:
            return jsonify(error=f"Video processing failed: {e}"), 400
        finally:
            os.remove(t.name)
    lane = request.form.get("emergency_lane", type=int)
    prev = request.form.get("prev")
    prev = [float(x) for x in prev.split(",")] if prev else counts
    lane = lane if lane is not None and 0 <= lane <= 3 else None
    return jsonify(plan(counts, prev, lane))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
