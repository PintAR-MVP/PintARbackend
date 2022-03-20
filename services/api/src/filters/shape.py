import traceback
import shapely.geometry as sg
import shapely.wkt as sw
import shapely.affinity as sa
import shapely.ops as so
from geographiclib.geodesic import Geodesic

from .filter import ScoreFilter

def normalize_polygon(polygon):
  polygon = sa.translate(polygon, -polygon.centroid.x, -polygon.centroid.y, 0)
  
  minx, miny, maxx, maxy = polygon.bounds
  scale = 1.0 / max(abs(minx), abs(miny), abs(maxx), abs(maxy))

  return sa.scale(polygon, scale, scale, 1.0, "centroid")

def _area_of_polygon(coords):
  geod = Geodesic.WGS84
  p = geod.Polygon()
  for coord in coords:
    lon, lat = coord

    p.AddPoint(lat, lon)

  num, perim, area = p.Compute()
  return abs(area)

def area_of_polygon(polygon):
  area = 0
  if polygon.type == "Polygon":
    area = _area_of_polygon(list(polygon.exterior.coords))
  elif polygon.type == "MultiPolygon":
    for p in list(polygon):
      area += _area_of_polygon(list(p.exterior.coords))

  return area

def intersection_ratio_of_polygons(polygon1, polygon2):
  union = so.unary_union([polygon1, polygon2])
  intersection = polygon1.intersection(polygon2)

  union_area = area_of_polygon(union)
  intersection_area = area_of_polygon(intersection)

  if union_area > 0.0 and intersection_area > 0.0:
    return (intersection_area / union_area)

  return 0.0

def shape_similarity_score(polygon1, polygon2):
  return intersection_ratio_of_polygons(polygon1, polygon2)

class ShapeFilter(ScoreFilter):
  def __init__(self, config):
    self.config = config

  def score(self, products):
    try:
      polygon = None
      
      if "shape" in self.config:
        shape = self.config["shape"]

        # Shapely requires polygons to start and end with the same point
        first_point = shape[0]
        last_point = shape[-1]
        if first_point[0] != last_point[0] or first_point[1] != last_point[1]:
          shape.append(first_point)

        polygon = sg.Polygon(shape)
      elif "wkt" in self.config:
        polygon = sw.loads(self.config.get("wkt"))
        assert polygon.type == "Polygon"
      else:
        assert False

      polygon = normalize_polygon(polygon)

      scores = []    
      for product in products:
        product_polygon = sw.loads(product["shape"])
        assert product_polygon.type == "Polygon"

        product_polygon = normalize_polygon(product_polygon)

        shape_score = shape_similarity_score(polygon, product_polygon)

        scores.append(shape_score)

      return scores
    except:
      traceback.print_exc()

      return [0.0] * len(products)