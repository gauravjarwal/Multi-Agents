"""
app.py  –  Flask REST API
─────────────────────────
Exposes two endpoints:
  POST /api/query       – synchronous agent pipeline
  POST /api/query/async – async pipeline via the message queue

Both accept  {"query": "..."}  and return the agents' response.
"""

import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import HOST, PORT, DEBUG
from agent_a import AgentA
from orchestrator import Orchestrator


# ── App setup ─────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # allow the JS frontend to call us

agent_a = AgentA()
orchestrator = Orchestrator()


# ── Routes ────────────────────────────────────────────────────────────

@app.route("/api/query", methods=["POST"])
def query_sync():
    """Synchronous endpoint — uses direct function calls between agents."""
    body = request.get_json(silent=True) or {}
    user_input = body.get("query", "").strip()

    if not user_input:
        return jsonify({"error": "Please provide a 'query' field."}), 400

    try:
        result = agent_a.process_request(user_input)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": f"Processing failed: {exc}"}), 500


@app.route("/api/query/async", methods=["POST"])
def query_async():
    """Async endpoint — routes messages through the MessageQueue."""
    body = request.get_json(silent=True) or {}
    user_input = body.get("query", "").strip()

    if not user_input:
        return jsonify({"error": "Please provide a 'query' field."}), 400

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(orchestrator.handle_request(user_input))
        loop.close()
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": f"Async processing failed: {exc}"}), 500


@app.route("/api/health", methods=["GET"])
def health():
    """Simple health-check endpoint."""
    return jsonify({"status": "ok", "agents": ["agent_a", "agent_b"]})


# ── Entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🚀  Multi-Agent API running on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
