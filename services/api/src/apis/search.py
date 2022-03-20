from flask_restx import Resource, Namespace, fields
from flask import request, abort

from filters import ColorFilter, TextFilter, ShapeFilter, CategoryFilter

api = Namespace("Search", description="Resources for product search from users.", validate=True)

TextFilterConfig = api.model("TextFilterConfig", {
  "text": fields.String(description="Text detected inside the image region the product was detected in.", required=True)
})

CategoryFilterConfig = api.model("CategoryFilterConfig", {
  "category": fields.String(description="Prediction of the product category.", required=True)
})

ColorFilterConfig = api.model("ColorFilterConfig", {
  "color": fields.String(description="Average color of the image region the product was detected in.", required=True)
})

ShapeFilterConfig = api.model("ShapeFilterConfig", {
  "wkt": fields.String(description="Detected product outline as a polygon in WKT representation.", required=False),
  "shape": fields.List(fields.List(fields.Float()), description="Detected product outline as an array of x, y coordinates.", required=False)
})

SearchRequest = api.model("SearchRequest", {
  "text_filter": fields.Nested(TextFilterConfig, description="Primary filter that is tested against all products in the Database.", required=True), 
  "color_filter": fields.Nested(ColorFilterConfig, description="Filter that is evaluated on the result of the primary filter.", required=False),
  "shape_filter": fields.Nested(ShapeFilterConfig, description="Filter that is evaluated on the result of the primary filter.", required=False),
  "category_filter": fields.Nested(CategoryFilterConfig, description="Filter that is evaluated on the result of the primary filter.", required=False),
  "score": fields.Float(description="Minimum score required to include a match in the response.", default=0.0, required=False),
  "limit": fields.Integer(description="Maximum number of matches to include in the response.", default=10, required=False)
})

Match = api.model("Match", {
  "id": fields.String(description="Id of the matching product.", required=True),
  "name": fields.String(description="Name of the matching product.", required=True),
  "score": fields.Float(description="Score of how well the product matches.", required=True)
})

SearchResponse = api.model("SearchResponse", {
  "matches": fields.List(fields.Nested(Match, required=True), required=True)
})

@api.route('')
class SearchResource(Resource):
  @api.expect(SearchRequest, validate=False)
  @api.response(200, "Success", SearchResponse)
  @api.response(400, "Validation error")
  @api.response(500, "Internal server error")
  def post(self):
    """Search for products"""
    text_filter_config = request.json.get("text_filter", None)
    color_filter_config = request.json.get("color_filter", None)
    shape_filter_config = request.json.get("shape_filter", None)
    category_filter_config = request.json.get("category_filter", None)
    min_score = request.json.get("score", 0.0)
    limit = request.json.get("limit", 10)

    if text_filter_config == None:
      abort(400)

    text_filter = TextFilter(text_filter_config)
    products, scores = text_filter.query()

    score_filters = []
    score_filter_weights = []

    if category_filter_config:
      category_filter = CategoryFilter(category_filter_config)
      score_filters.append(category_filter)
      score_filter_weights.append(0.0)

    if color_filter_config:
      color_filter = ColorFilter(color_filter_config)
      score_filters.append(color_filter)
      score_filter_weights.append(0.2)

    if shape_filter_config:
      shape_filter = ShapeFilter(shape_filter_config)
      score_filters.append(shape_filter)
      score_filter_weights.append(0.8)

    query_filter_weight = 0.5

    cum_filter_weights = sum(score_filter_weights) + query_filter_weight

    scores = [x * (query_filter_weight / cum_filter_weights) for x in scores]
    for score_filter, score_filter_weight in zip(score_filters, score_filter_weights):
      filter_scores = score_filter.score(products)

      for idx, x in enumerate(filter_scores):
        scores[idx] += x * (score_filter_weight / cum_filter_weights)

    matches = []
    for product, score in zip(products, scores):
      if score < min_score:
        continue

      match = {}
      match["id"] = product["id"]
      match["name"] = product["name"]
      match["score"] = score
      matches.append(match)

    matches.sort(key=lambda x: x["score"], reverse=True)

    if len(matches) > limit:
      matches = matches[:limit]

    return { "matches": matches }, 200