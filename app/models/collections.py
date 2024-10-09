import json
from pathlib import Path

class Collection:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        self.features = self.load_features()

    def load_features(self):
        with open(self.data_path) as f:
            geojson_data = json.load(f)
        return geojson_data['features']

    def get_feature(self, feature_id):
        for feature in self.features:
            if feature.get('properties', {}).get('name') == feature_id:
                return feature
        return None
