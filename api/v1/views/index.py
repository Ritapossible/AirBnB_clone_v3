#!/usr/bin/python3
"""API endpoint for /api/v1/"""
from flask import jsonify
from api.v1.views import app_views
from models import storage
from models.engine.db_storage import classes


# Create a route /status that returns JSON
@app_views.route("/status", methods=["GET"], strict_slashes=False)
def status():
    """retrieves the status of the api"""
    return jsonify({"status": "OK"})


@app_views.route("/stats", methods=["GET"], strict_slashes=False)
def stats():
    """retrieves the number of obj in eac class"""
    new_dict = {}

    for _, value in classes.items():
        count = storage.count(value)
        new_dict[value.__tablename__] = count
    return jsonify(new_dict)
