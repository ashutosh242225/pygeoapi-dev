# routes.py

from flask import Flask, jsonify, request, Response
from config import COLLECTIONS_CONFIG
from data_loader import load_data_from_sql, load_data_from_geojson,simplify_geojson
import os
from jobs import create_job, get_job_status
import gzip
import json
from shapely.geometry import shape, Point, Polygon, box
from flask_geojson import GeoJSON

app = Flask(__name__)

def initialize_routes(app):
    @app.route("/collections", methods=["GET"])
    def get_collections():
        collections = [{"id": collection["id"], "title": collection["title"], "description": collection.get("description", "")} for collection in COLLECTIONS_CONFIG["collections"]]
        return jsonify({"collections": collections})
    
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
        return jsonify({"id": collection_id, "title": collection["title"], "description": collection.get("description", "")})
   
    '''@app.route("/collections/<collection_id>/items", methods=["GET"])
    def get_features(collection_id):
        collection = next((c for c in COLLECTIONS_CONFIG["collections"] if c["id"] == collection_id), None)
        if not collection:
            return jsonify({"error": "Collection not found"}), 404
        # Add logic to load data from the appropriate source
        if collection["type"] == "geojson":
            features = load_data_from_geojson(collection["file_path"])
        elif collection["type"] == "sql":
            features = load_data_from_sql(collection["connection_string"], collection["table"])
        else:
            return jsonify({"error": "Unsupported collection type"}), 400
        simplified_features = simplify_geojson(features)
        compressed_data = gzip.compress(json.dumps(simplified_features).encode('utf-8'))
        return Response(compressed_data, content_type='application/json', headers={'Content-Encoding': 'gzip'})'''
    
    @app.route("/collections/<collection_id>/items", methods=["GET"])
    def get_features(collection_id):
        zoom = int(request.args.get('zoom'))
        bbox = request.args.get('bbox')

        if not zoom:
            return jsonify({"error": "Zoom parameter is required"}), 400
        if not bbox:
            return jsonify({"error": "Bbox parameter is required"}), 400

        bbox = [float(coord) for coord in bbox.split(',')]
        bbox_polygon = box(bbox[0], bbox[1], bbox[2], bbox[3])

        collection = next((c for c in COLLECTIONS_CONFIG["collections"] if c["id"] == collection_id), None)
        if not collection:
            return jsonify({"error": "Collection not found"}), 404

        if collection["type"] == "geojson":
            features = load_data_from_geojson(collection["file_path"])
        elif collection["type"] == "sql":
            features = load_data_from_sql(collection["connection_string"], collection["table"])
        else:
            return jsonify({"error": "Unsupported collection type"}), 400

        # Get zoom levels for the collection
        zoom_levels = collection.get("zoom_levels", {})

        # Determine the level based on the zoom level
        level = None
        for lvl, (min_zoom, max_zoom) in zoom_levels.items():
            if min_zoom <= zoom <= max_zoom:
                level = lvl
                break

        if not level:
            return jsonify({"error": "No matching level for the given zoom"}), 400

        filtered_features = [f for f in features["features"] if f["properties"].get("level") == level]
        filtered_features = [f for f in filtered_features if shape(f["geometry"]).intersects(bbox_polygon)]
        
        # Include feature ID in the response
        for feature in filtered_features:
            feature["properties"]["feature_id"] = feature["properties"]["id"]
        
        return jsonify({"type": "FeatureCollection", "features": filtered_features})

    @app.route("/collections/<collection_id>/items/<feature_id>", methods=["GET"])
    def get_feature_by_id(collection_id, feature_id):
        collection = next((c for c in COLLECTIONS_CONFIG["collections"] if c["id"] == collection_id), None)
        if not collection:
            return jsonify({"error": "Collection not found"}), 404
        # Add logic to load data from the appropriate source
        if collection["type"] == "geojson":
            features = load_data_from_geojson(collection["file_path"])
        elif collection["type"] == "sql":
            features = load_data_from_sql(collection["connection_string"], collection["table"])
        else:
            return jsonify({"error": "Unsupported collection type"}), 400
        
        feature = next((f for f in features["features"] if f["properties"]["id"] == int(feature_id)), None)
        if not feature:
            return jsonify({"error": "Feature not found"}), 404
        return jsonify(feature)
    
    @app.route("/collections/<collection_id>/items/administrative", methods=["GET"])
    def get_administrative_boundaries(collection_id):
        zoom = int(request.args.get('zoom'))
        bbox = request.args.get('bbox')

        if not zoom:
            return jsonify({"error": "Zoom parameter is required"}), 400

        bbox_polygon = None
        if bbox:
            bbox = [float(coord) for coord in bbox.split(',')]
            bbox_polygon = box(bbox[0], bbox[1], bbox[2], bbox[3])

        collection = next((c for c in COLLECTIONS_CONFIG["collections"] if c["id"] == collection_id), None)
        if not collection:
            return jsonify({"error": "Collection not found"}), 404

        if collection["type"] == "geojson":
            features = load_data_from_geojson(collection["file_path"])
        elif collection["type"] == "sql":
            features = load_data_from_sql(collection["connection_string"], collection["table"])
        else:
            return jsonify({"error": "Unsupported collection type"}), 400

        # Get zoom levels for the collection
        zoom_levels = collection.get("zoom_levels", {})

        # Determine the level based on the zoom level
        level = None
        for lvl, (min_zoom, max_zoom) in zoom_levels.items():
            if min_zoom <= zoom <= max_zoom:
                level = lvl
                break

        if not level:
            return jsonify({"error": "No matching level for the given zoom"}), 400

        filtered_features = [f for f in features["features"] if f["properties"].get("level") == level]
        if bbox_polygon:
            filtered_features = [f for f in filtered_features if shape(f["geometry"]).intersects(bbox_polygon)]
        
        # Include feature ID in the response
        for feature in filtered_features:
            feature["properties"]["feature_id"] = feature["properties"]["id"]
        
        return jsonify({"type": "FeatureCollection", "features": filtered_features})

    @app.route("/collections/<collection_id>/items/point", methods=["GET"])
    def get_point_features(collection_id):
        zoom = int(request.args.get('zoom'))
        bbox = request.args.get('bbox')

        if not zoom:
            return jsonify({"error": "Zoom parameter is required"}), 400

        bbox_polygon = None
        if bbox:
            bbox = [float(coord) for coord in bbox.split(',')]
            bbox_polygon = box(bbox[0], bbox[1], bbox[2], bbox[3])

        collection = next((c for c in COLLECTIONS_CONFIG["collections"] if c["id"] == collection_id), None)
        if not collection:
            return jsonify({"error": "Collection not found"}), 404

        if collection["type"] == "geojson":
            features = load_data_from_geojson(collection["file_path"])
        elif collection["type"] == "sql":
            features = load_data_from_sql(collection["connection_string"], collection["table"])
        else:
            return jsonify({"error": "Unsupported collection type"}), 400

        filtered_features = [f for f in features["features"] if f["properties"].get("min_zoom", 0) <= zoom <= f["properties"].get("max_zoom", 20) and shape(f["geometry"]).geom_type == 'Point']
        if bbox_polygon:
            filtered_features = [f for f in filtered_features if shape(f["geometry"]).intersects(bbox_polygon)]
        
        # Include feature ID in the response
        for feature in filtered_features:
            feature["properties"]["feature_id"] = feature["properties"]["id"]
        
        return jsonify({"type": "FeatureCollection", "features": filtered_features})

    
    @app.route("/collections/<collection_id>/items/polygon", methods=["GET"])
    def get_polygon_features(collection_id):
        zoom = int(request.args.get('zoom'))
        bbox = request.args.get('bbox')

        if not zoom:
            return jsonify({"error": "Zoom parameter is required"}), 400
        if not bbox:
            return jsonify({"error": "Bbox parameter is required"}), 400

        bbox = [float(coord) for coord in bbox.split(',')]
        bbox_polygon = box(bbox[0], bbox[1], bbox[2], bbox[3])

        collection = next((c for c in COLLECTIONS_CONFIG["collections"] if c["id"] == collection_id), None)
        if not collection:
            return jsonify({"error": "Collection not found"}), 404

        if collection["type"] == "geojson":
            features = load_data_from_geojson(collection["file_path"])
        elif collection["type"] == "sql":
            features = load_data_from_sql(collection["connection_string"], collection["table"])
        else:
            return jsonify({"error": "Unsupported collection type"}), 400

        filtered_features = [f for f in features["features"] if f["properties"].get("min_zoom", 0) <= zoom <= f["properties"].get("max_zoom", 20)]
        filtered_features = [f for f in filtered_features if shape(f["geometry"]).intersects(bbox_polygon)]
        
        # Include feature ID in the response
        for feature in filtered_features:
            feature["properties"]["feature_id"] = feature["properties"]["id"]
        
        return jsonify({"type": "FeatureCollection", "features": filtered_features})

    
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