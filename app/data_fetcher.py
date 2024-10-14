# data_fetcher.py
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from shapely.geometry import mapping, shape
import json

Base = declarative_base()

class Feature(Base):
    __tablename__ = 'features'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    geom = Column(Geometry('POLYGON'))

def fetch_data_from_db(session):
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