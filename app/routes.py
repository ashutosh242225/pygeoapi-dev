# routes.py
from flask import Flask, jsonify, request
from .models.collections import Collection
from app.jobs import create_job, get_job_status
from data_combiner import combine_data
import os

app = Flask(__name__)

# Load the collection data
collection_path = os.path.join(os.path.dirname(__file__), 'data', 'example_collection.geojson')
collection = Collection(collection_path)

def initialize_routes(app):
    # OGC Features Routes
    @app.route("/collections", methods=["GET"])
    def get_collections():
        return jsonify([{"id": "example_collection", "title": "Example Collection"}])
    
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
        if collection_id != "example_collection":
            return jsonify({"error": "Collection not found"}), 404
        return jsonify({"id": collection_id, "title": "Example Collection", "description": "Sample MultiPolygon feature."})

    @app.route("/collections/<collection_id>/features", methods=["GET"])
    def get_features(collection_id):
        if collection_id != "example_collection":
            return jsonify({"error": "Collection not found"}), 404
        return jsonify(collection.features)

    @app.route("/collections/<collection_id>/features/<feature_id>", methods=["GET"])
    def get_feature(collection_id, feature_id):
        if collection_id != "example_collection":
            return jsonify({"error": "Collection not found"}), 404
        feature = collection.get_feature(feature_id)
        if not feature:
            return jsonify({"error": "Feature not found"}), 404
        return jsonify(feature)

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

    # Route to serve combined data from SQL Server and GeoJSON
    @app.route("/collections/combined", methods=["GET"])
    def get_combined_collections():
        geojson_file_path = os.path.join(os.path.dirname(__file__), 'data', 'example_collection.geojson')
        combined_data = combine_data(geojson_file_path)
        return jsonify(combined_data)

if __name__ == "__main__":
    initialize_routes(app)
    app.run(debug=True)