"""Minimal Flask app for PythonAnywhere — serves index.html, app.js, and data/.

PythonAnywhere requires a WSGI entrypoint even for nearly-static sites.
This module is referenced from the PA Web tab → WSGI config:

    import sys
    path = '/home/<USERNAME>/thai-oil-prices'
    if path not in sys.path:
        sys.path.insert(0, path)
    from flask_app import app as application
"""
import os
from flask import Flask, send_from_directory, abort

ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_TOP = {"app.js", "index.html", "data"}

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.route("/<path:relpath>")
def passthrough(relpath: str):
    # URL paths always use '/'. Disallow traversal.
    parts = relpath.split("/")
    if ".." in parts or relpath.startswith("/"):
        abort(404)
    if parts[0] not in ALLOWED_TOP:
        abort(404)
    return send_from_directory(ROOT, relpath)


if __name__ == "__main__":
    app.run(debug=True)
