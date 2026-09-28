"""Simple web page: python web.py  ->  http://127.0.0.1:5000"""
import re
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from workflow import build_graph, resume, start

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
GRAPH = build_graph()  # one in-memory checkpointer shared by all requests


@app.get("/")
def index():
    return send_from_directory(ROOT / "static", "index.html")


@app.get("/api/sample/<pid>")
def sample(pid):
    path = ROOT / "data" / f"{pid}.txt"
    if not re.fullmatch(r"P\d{3}", pid) or not path.is_file():
        return jsonify(error="No sample note for that ID"), 404
    return jsonify(note=path.read_text())


@app.post("/api/review")
def review():
    body = request.get_json(force=True)
    if not (body.get("patient_id") or "").strip() or not (body.get("note") or "").strip():
        return jsonify(status="error", error="Patient ID and clinical note are required."), 400
    return jsonify(start(GRAPH, body["patient_id"].strip(), body["note"]))


@app.post("/api/decision")
def decision():
    body = request.get_json(force=True)
    try:
        return jsonify(resume(GRAPH, body.get("thread_id", ""), body.get("answer", "no")))
    except Exception as e:
        return jsonify(status="error", error=str(e)), 400


if __name__ == "__main__":
    app.run(debug=False)
