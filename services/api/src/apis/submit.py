from flask_restx import Resource, Namespace, fields
from flask import request, abort

import os
import boto3
import json
import uuid

from common.utility.s3 import create_presigned_url

api = Namespace("Submit", description="Resources for product submissions from users and the processing of these submissions from admins.")

SubmitImage = api.model("SubmitImage", {
  "key": fields.String(description="ID to later reference this image.", required=True),
  "upload_url": fields.String(description="Signed URL that must be used to upload the image.", required=True)
})

ValidationTask = api.model("ValidationTask", {
  "images": fields.List(fields.String(description="Signed URL that can be used to download the image", required=True), required=True),
  "name": fields.String(description="Suggestion for the product name."),
  "color": fields.String(description="Suggestion for the product color."),
  "category": fields.String(description="Suggestion for the product category."),
  "shape": fields.String(description="Suggestion for the product outline as a polygon in WKT representation."),
  "label_text": fields.String(description="Suggestion for the product label text.")
})

SubmitProductPostRequest = api.model("SubmitProductPostRequest", {
  "images": fields.List(fields.String(description="ID of a previously submitted image.", required=True), required=True),
  "name": fields.String(description="Suggestion for the product name."),
  "color": fields.String(description="Suggestion for the product color."),
  "category": fields.String(description="Suggestion for the product category."),
  "shape": fields.String(description="Suggestion for the product outline as a polygon in WKT representation."),
  "label_text": fields.String(description="Suggestion for the product label text.")
})

SubmitProductImagesPostRequest = api.model("SubmitProductImagesPostRequest", {
  "count": fields.Integer(description="Number of images to submit.", min=0)
})

SubmitProductImagesPostResponse = api.model("SubmitProductImagesPostResponse", {
  "images": fields.List(fields.Nested(SubmitImage, required=True), required=True)
})

SubmitValidationGetResponse = api.model("SubmitValidationGetResponse", {
  "task_id": fields.String(description="ID to later reference this validation task.", required=True),
  "task_data": fields.Nested(ValidationTask, required=True)
})

SubmitValidationDeleteRequest = api.model("SubmitValidationDeleteRequest", {
  "task_id": fields.String(description="ID of the validation task that should be deleted(marked as done).")
})

@api.route("/product")
class SubmitProductResource(Resource):
  @api.expect(SubmitProductPostRequest, validate=False)
  @api.response(200, "Success")
  @api.response(400, "Validation error")
  @api.response(500, "Internal server error")
  def post(self):
    """Submit a product"""
    if "images" not in request.json:
      abort(400)

    upload_id = str(uuid.uuid4())

    try:
      sqs = boto3.client("sqs")
      sqs.send_message(
        QueueUrl=os.environ.get("PRODUCTS_UPLOAD_QUEUE_URL"),
        MessageBody=json.dumps({
          "name": request.json.get("name", None),
          "images": request.json["images"],
          "label_text": request.json.get("label_text", None),
          "color": request.json.get("color", None),
          "category": request.json.get("category", None),
          "shape": request.json.get("shape", None)
        }),
        MessageDeduplicationId=upload_id,
        MessageGroupId=upload_id
      )
    except Exception as e:
      print(f"Can't upload product due to {str(e)}")
      abort(500)

    return {}, 200

@api.route("/product-image")
class SubmitProductImagesResource(Resource):
  @api.expect(SubmitProductImagesPostRequest, validate=False)
  @api.response(200, "Success", SubmitProductImagesPostResponse)
  @api.response(500, "Internal server error")
  def post(self):
    """Submit product images"""
    count = request.json.get("count", 1)

    images = []
    for i in range(0, count):
      key = str(uuid.uuid4())
      upload_url = create_presigned_url(os.environ.get("IMAGE_UPLOAD_BUCKET_NAME"), key, "put_object", 900)
      images.append({ 
          "key": key,
          "upload_url": upload_url
      })

    return { 
      "images": images
    }, 200

@api.route("/validate")
class SubmitValidationResource(Resource):
  @api.response(200, "Success", SubmitValidationGetResponse)
  @api.response(204, "No pending validation task")
  @api.response(500, "Internal server error")
  def get(self):
    """Request a validation task"""
    sqs = boto3.client("sqs")
    response = sqs.receive_message(
      QueueUrl=os.environ.get("PRODUCTS_UPLOAD_QUEUE_URL"),
      VisibilityTimeout=900,
      WaitTimeSeconds=0,
      MaxNumberOfMessages=1
    )

    if "Messages" not in response or len(response["Messages"]) == 0:
      return {}, 204

    message = response["Messages"][0]

    task_id = message["ReceiptHandle"]
    task_data = json.loads(message["Body"])
    if "images" in task_data:
      task_data["images"] = [
        create_presigned_url(os.environ.get("IMAGE_UPLOAD_BUCKET_NAME"), image, "get_object", 900) for image in task_data["images"]
      ]

    return {
      "task_id": task_id,
      "task_data": task_data
    }, 200

  @api.expect(SubmitValidationDeleteRequest, validate=False)
  @api.response(200, "Success")
  @api.response(400, "Validation error")
  @api.response(500, "Internal server error")
  def delete(self):
    """Mark the validation task as done."""
    if "task_id" not in request.json:
      abort(400)

    try:
      sqs = boto3.client("sqs")
      sqs.delete_message(
        QueueUrl=os.environ.get("PRODUCTS_UPLOAD_QUEUE_URL"),
        ReceiptHandle=request.json["task_id"]
      )
    except Exception as e:
      print(f"Can't reject cleansing due to {e}.")
      abort(500)      

    return {}, 200