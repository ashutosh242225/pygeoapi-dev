# data_loader.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from shapely.geometry import mapping, shape
import json

Base = declarative_base()

'''class Feature(Base):
    __tablename__ = 'features'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    geom = Column(Geometry('POLYGON'))'''

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
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data