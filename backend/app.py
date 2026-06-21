"""Gamma Exposure Heatmap - Flask API.

Dev:  run this (port 5001) + `npm run dev` in ../frontend.
Prod: `npm run build` in ../frontend, then this serves it at /.
"""
import os
from flask import Flask, jsonify, send_from_directory

import marketdata
import heatmap

DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
app = Flask(__name__, static_folder=None)


@app.route("/api/heatmap")
def api_heatmap():
    spot = 5500.0
    return jsonify(heatmap.payload(marketdata.get_chain(spot=spot), spot))


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    full = os.path.join(DIST, path)
    if path and os.path.exists(full):
        return send_from_directory(DIST, path)
    if os.path.exists(os.path.join(DIST, "index.html")):
        return send_from_directory(DIST, "index.html")
    return ("Frontend not built. Run `npm install && npm run dev` in ../frontend.", 200)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5001)))
