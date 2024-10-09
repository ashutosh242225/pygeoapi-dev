from shapely.geometry import Polygon, LineString, Point, GeometryCollection, shape, mapping

class BufferProcess:
    def execute(self, feature, distance):
        geom = shape(feature['geometry'])
        if not isinstance(geom, (Polygon, LineString, Point, GeometryCollection)):
            raise ValueError("Input geometry must be a Polygon, LineString, Point, or GeometryCollection")
        buffered_geom = geom.buffer(distance)
        return {
            "type": "Feature",
            "geometry": mapping(buffered_geom),
            "properties": feature.get('properties', {})
        }

class IntersectionProcess:
    def execute(self, feature1, feature2):
        geom1 = shape(feature1['geometry'])
        geom2 = shape(feature2['geometry'])
        if not isinstance(geom1, (Polygon, LineString, Point, GeometryCollection)) or not isinstance(geom2, (Polygon, LineString, Point, GeometryCollection)):
            raise ValueError("Input geometries must be Polygon, LineString, Point, or GeometryCollection")
        intersection_geom = geom1.intersection(geom2)
        return {
            "type": "Feature",
            "geometry": mapping(intersection_geom),
            "properties": {**feature1.get('properties', {}), **feature2.get('properties', {})}
        }

class DifferenceProcess:
    def execute(self, feature1, feature2):
        geom1 = shape(feature1['geometry'])
        geom2 = shape(feature2['geometry'])
        if not isinstance(geom1, (Polygon, LineString, Point, GeometryCollection)) or not isinstance(geom2, (Polygon, LineString, Point, GeometryCollection)):
            raise ValueError("Input geometries must be Polygon, LineString, Point, or GeometryCollection")
        difference_geom = geom1.difference(geom2)
        return {
            "type": "Feature",
            "geometry": mapping(difference_geom),
            "properties": feature1.get('properties', {})
        }