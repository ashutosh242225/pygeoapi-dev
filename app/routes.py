# routes.py
from flask import Flask, jsonify, request
from config import COLLECTIONS_CONFIG
from data_loader import load_data_from_sql, load_data_from_geojson
import os
from jobs import create_job, get_job_status

app = Flask(__name__)

def initialize_routes(app):
    # OGC Features Routes
    @app.route("/collections", methods=["GET"])
    def get_collections():
        collections = [{"id": collection["id"], "title": collection["id"]} for collection in COLLECTIONS_CONFIG["collections"]]
        return jsonify(collections)
    
    @app.route("/conformance", methods=["GET"])
    def get_conformance():
        return jsonify({
            "conformsTo": [
                "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
                "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"
            ]
        })

    @app.route("/collections/<collection_id>", methods=["GET"])
    def get_collection(collection_id):
        collection = next((c for c in COLLECTIONS_CONFIG["collections"] if c["id"] == collection_id), None)
        if not collection:
            return jsonify({"error": "Collection not found"}), 404
        return jsonify({"id": collection_id, "title": collection_id, "description": f"Collection from {collection['type']} source."})

    @app.route("/collections/<collection_id>/features", methods=["GET"])
    def get_features(collection_id):
        collection = next((c for c in COLLECTIONS_CONFIG["collections"] if c["id"] == collection_id), None)
        if not collection:
            return jsonify({"error": "Collection not found"}), 404
        
        if collection["type"] == "sql":
            data = load_data_from_sql(collection["connection_string"], collection["table"])
        elif collection["type"] == "geojson":
            data = load_data_from_geojson(collection["file_path"])
        else:
            return jsonify({"error": "Unsupported collection type"}), 400
        
        return jsonify(data)

    # OGC Processes Routes
    @app.route("/processes", methods=["GET"])
    def get_processes():
        return jsonify([
            {
                "id": "buffer",
                "title": "Buffer Process",
                "description": "Buffers geometries by a given distance."
            },
            {
                "id": "intersection",
                "title": "Intersection Process",
                "description": "Finds the intersection of two geometries."
            },
            {
                "id": "difference",
                "title": "Difference Process",
                "description": "Finds the difference between two geometries."
            },
            {
                "id": "near",
                "title": "Near Process",
                "description": "Finds the nearest feature in a collection to the input feature."
            }
        ])

    @app.route("/processes/buffer/jobs", methods=["POST"])
    def create_buffer_job():
        input_data = request.json
        job_id = create_job("buffer", input_data)
        return jsonify({"job_id": job_id, "status": "running"})

    @app.route("/processes/intersection/jobs", methods=["POST"])
    def create_intersection_job():
        input_data = request.json
        if 'feature1' not in input_data or 'feature2' not in input_data:
            return jsonify({"error": "Both 'feature1' and 'feature2' are required"}), 400
        job_id = create_job("intersection", input_data)
        return jsonify({"job_id": job_id, "status": "running"})

    @app.route("/processes/difference/jobs", methods=["POST"])
    def create_difference_job():
        input_data = request.json
        if 'feature1' not in input_data or 'feature2' not in input_data:
            return jsonify({"error": "Both 'feature1' and 'feature2' are required"}), 400
        job_id = create_job("difference", input_data)
        return jsonify({"job_id": job_id, "status": "running"})

    @app.route("/processes/near/jobs", methods=["POST"])
    def create_near_job():
        input_data = request.json
        job_id = create_job("near", input_data)
        return jsonify({"job_id": job_id, "status": "running"})

    @app.route("/jobs/<job_id>", methods=["GET"])
    def get_job(job_id):
        job = get_job_status(job_id)
        return jsonify(job)
    
    # OGC Styles Routes
    @app.route("/styles", methods=["GET"])
    def get_styles():
        return jsonify([{"id": "example_style", "title": "Example Style"}])

    @app.route("/styles/<style_id>", methods=["GET"])
    def get_style(style_id):
        if style_id != "example_style":
            return jsonify({"error": "Style not found"}), 404
        return jsonify({"style": "Returned style"})

if __name__ == "__main__":
    initialize_routes(app)
    app.run(debug=True)