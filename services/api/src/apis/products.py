from pydoc import describe
from flask_restx import Resource, Namespace, fields
from flask import request, abort

from common.models import Products
from common.utility.s3 import delete_from_s3, copy_s3

import uuid
import os

api = Namespace("Products", description="Resources for admins to perform CRUD operations on products.")

Product = api.model("Product", {
  "id": fields.String(description="Unique ID that can be used to later reference this product.", required=True),
  "creation_date": fields.DateTime(description="Date when the product was added to the database.", required=True),
  "name": fields.String(description="Name of the product.", required=True),
  "category": fields.String(description="Category of the product.", required=True),
  "label_text": fields.String(description="Text visible on the product label.", required=True),
  "images": fields.List(fields.String(description="Unique ID of a image attached to this product.", required=True), required=True),
  "shape": fields.String(description="Outline of the product as a polygon in its WKT representation.", required=True),
  "color": fields.String(describtion="Color of the product.", required=True)
})

ProductsPostRequest = api.model("ProductsPostRequest", {
  "name": fields.String(description="Name.", required=True),
  "category": fields.String(description="Category of the product.", required=True),
  "label_text": fields.String(description="Text visible on the product label.", required=True),
  "images": fields.List(fields.String(description="ID of a previously submitted image.", required=True), required=True),
  "shape": fields.String(description="Outline of the product as a polygon in its WKT representation.", required=True),
  "color": fields.String(describtion="Color of the product.", required=True)
})

ProductPutRequest = api.model("ProductPutRequest", {
  "name": fields.String(description="New name of the product."),
  "category": fields.String(description="New category of the product."),
  "label_text": fields.String(description="New text that is visible on the product label."),
  "shape": fields.String(description="New outline of the product as a polygon in its WKT representation."),
  "color": fields.String(describtion="New color of the product.")
})

ProductImagesPostRequest = api.model("ProductImagesPostRequest", {
  "images": fields.List(fields.String(description="ID of a previously submitted image.", required=True), required=True)
})

ProductsPostResponse = api.model("ProductsPostResponse", {
  "product": fields.Nested(Product, required=True)
})

ProductGetResponse = api.model("ProductGetResponse", {
  "product": fields.Nested(Product, required=True)
})

ProductPutResponse = api.model("ProductPutResponse", {
  "product": fields.Nested(Product, required=True)
})

@api.route("")
class ProductsResource(Resource):
  @api.expect(ProductsPostRequest, validate=False)
  @api.response(200, "Success", ProductsPostResponse)
  @api.response(400, "Validation error")
  @api.response(500, "Internal server error")
  def post(self):
    """Create a new product"""
    if "images" not in request.json:
      abort(400)

    if "name" not in request.json:
      abort(400)

    if "label_text" not in request.json:
      abort(400)

    if "shape" not in request.json:
      abort(400)

    if "color" not in request.json:
      abort(400)

    if "category" not in request.json:
      abort(400)

    try:
      product = Products()

      product.images = []

      for image in request.json["images"]:
        key = f"{product.id}/{uuid.uuid4()}"

        copy_s3(
          os.environ.get("IMAGE_UPLOAD_BUCKET_NAME"),
          image,
          os.environ.get("PRODUCTS_BUCKET_NAME"),
          key
        )

        product.images.append(key)

      product.name = request.json["name"]
      product.category = request.json["category"]
      product.label_text = request.json["label_text"]
      product.shape = request.json["shape"]
      product.color = request.json["color"]

      product.commit()
    except Exception as e:
      print(f"Can't create product due to {e}.")
      abort(500)  
    return {"product": product.as_dict() }, 200   

@api.route("/<product_id>")
@api.doc(params={"product_id": "ID of the product"})
class ProductResource(Resource):
  @api.response(200, "Success", ProductGetResponse)
  @api.response(404, "Product not found")
  @api.response(500, "Internal server error")
  def get(self, product_id):
    """Get a product"""
    try:
      product = Products.get_by_id(product_id)
    except:
      abort(404)
      
    return {"product": product.as_dict() }, 200

  @api.expect(ProductPutRequest, validate=False)
  @api.response(200, "Success", ProductPutResponse)
  @api.response(404, "Product not found")
  @api.response(500, "Internal server error")
  def put(self, product_id):
    """Update a product"""
    try:
      product = Products.get_by_id(product_id)
    except:
      abort(404)

    if "name" in request.json:
      product.name = request.json["name"]

    if "label_text" in request.json:
      product.label_text = request.json["label_text"]

    if "shape" in request.json:
      product.shape = request.json["shape"]

    if "color" in request.json:
      product.color = request.json["color"]

    if "category" in request.json:
      product.category = request.json["category"]

    product.commit()

    return { "product": product.as_dict() }, 200

  @api.response(200, "Success")
  @api.response(404, "Product not found")
  @api.response(500, "Internal server error")
  def delete(self, product_id):
    """Delete a product"""
    try:
      product = Products.get_by_id(product_id)
    except:
      abort(404)

    product.delete()
    product.commit()

    return {}, 200

@api.route("/<product_id>/images")
@api.doc(params={"product_id": "ID of the product"})
class ProductImagesResource(Resource):
  @api.expect(ProductImagesPostRequest, validate=False)
  @api.response(200, "Success")
  @api.response(400, "Validation error")
  @api.response(404, "Product not found")
  @api.response(500, "Internal server error")
  def post(self, product_id):
    """Attach images to a product"""
    if "images" not in request.json:
      abort(400)

    try:
      product = Products.get_by_id(product_id)
    except:
      abort(404)

    if not product.images:
      product.images = []

    for image in request.json["images"]:
      key = f"{product.id}/{uuid.uuid4()}"

      copy_s3(
        os.environ.get("IMAGE_UPLOAD_BUCKET_NAME"),
        image,
        os.environ.get("PRODUCTS_BUCKET_NAME"),
        key
      )

      product.images.append(key)

    product.commit()

    return {}, 200

@api.route("/<product_id>/images/<image_id>")
@api.doc(params={"product_id": "ID of the product", "image_id": "ID of the attached image"})
class ProductImageResource(Resource):
  @api.response(200, "Success")
  @api.response(404, "Image or product not found")
  @api.response(500, "Internal server error")
  def delete(self, product_id, image_id):
    """Remove attached images from a product"""
    try:
      product = Products.get_by_id(product_id)
    except:
      abort(404)

    if image_id not in product.images:
      abort(404)

    product.images = [x for x in product.images if x != image_id]

    try:
      delete_from_s3(os.environ.get("PRODUCTS_BUCKET_NAME"), f"{product_id}/{image_id}")
    except:
      pass

    product.commit()

    return {}, 200




          
