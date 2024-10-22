## data_loader.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from shapely.geometry import mapping, shape
import json
import os

Base = declarative_base()

class Feature(Base):
    __tablename__ = 'features'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    geom = Column(Geometry('POLYGON'))

def simplify_geojson(geojson_data, tolerance=0.01):
    simplified_features = []
    for feature in geojson_data['features']:
        geom = shape(feature['geometry'])
        simplified_geom = geom.simplify(tolerance, preserve_topology=True)
        feature['geometry'] = mapping(simplified_geom)
        simplified_features.append(feature)
    geojson_data['features'] = simplified_features
    return geojson_data

def load_data_from_sql(connection_string, table):
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    features = session.query(Feature).all()
    geojson_features = []
    for feature in features:
        geom = shape(feature.geom)
        geojson_feature = {
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "id": feature.id,
                "name": feature.name
            }
        }
        geojson_features.append(geojson_feature)
    return {
        "type": "FeatureCollection",
        "features": geojson_features
    }
def load_data_from_geojson(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file or directory: '{file_path}'")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data