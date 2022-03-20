import os

if os.environ.get("IS_OFFLINE"):
  os.environ["REGION"]="eu-central-1"
  os.environ["PRODUCTS_TABLE_NAME"]="pintar-api-products-prod"
  os.environ["PRODUCTS_BUCKET_NAME"]="pintar-api-products-prod"
  os.environ["IMAGE_UPLOAD_BUCKET_NAME"]="pintar-api-image-upload-prod"
  os.environ["PRODUCTS_UPLOAD_QUEUE_URL"]="https://sqs.eu-central-1.amazonaws.com/235501516910/pintar-api-products-upload-prod.fifo"
  os.environ["OPENSEARCH_ENDPOINT"]="search-pintar-api-prod-4bwhfqml63e7zkdjoyxh65mu3q.eu-central-1.es.amazonaws.com"

from flask import Flask
from flask_cors import CORS

from apis import api

app = Flask(__name__)
CORS(app, supports_credentials=True)

api.init_app(app)