# data_combiner.py
from db import get_db_session
from data_fetcher import fetch_data_from_db
from geojson_loader import load_geojson

def combine_data(geojson_file_path):
    session = get_db_session()
    db_data = fetch_data_from_db(session)
    geojson_data = load_geojson(geojson_file_path)
    
    combined_features = db_data["features"] + geojson_data["features"]
    combined_collection = {
        "type": "FeatureCollection",
        "features": combined_features
    }
    
    return combined_collection