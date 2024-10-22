# cache.py
import redis
import json

cache = redis.Redis(host='localhost', port=6379, db=0)

def cache_geojson(key, geojson_data):
    cache.set(key, json.dumps(geojson_data))

def get_cached_geojson(key):
    cached_data = cache.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None