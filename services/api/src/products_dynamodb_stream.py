import sys; import os; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import traceback
from opensearchpy import OpenSearch, RequestsHttpConnection
import boto3
import os
import json
from requests_aws4auth import AWS4Auth

from common.utility.dynamodb import from_dynamodb_json

def index_elasticsearch(data):
  try:
    session = boto3.Session()
    credentials = session.get_credentials()

    awsauth = AWS4Auth(
      credentials.access_key,
      credentials.secret_key,
      session.region_name, "es",
      session_token=credentials.token
    )

    es = OpenSearch(
      [{"host": os.environ.get("OPENSEARCH_ENDPOINT"), "port": 443}],
      http_auth=awsauth,
      use_ssl=True,
      verify_certs=True,
      connection_class=RequestsHttpConnection
    )

    if not es.indices.exists("products"):
      es.indices.create("products", body={
        "settings": {
          "index.mapping.coerce": True,
        },
        "mappings": {
          "properties": {
            "id": {
              "type": "keyword"
            }
          }
        }
      })

    es.index(
      index="products",
      body=data,
      id=data["id"],
      refresh=True
    )
  except Exception as e:
    # TODO: Figure out a better way to handle elasticsearch sync errors
    pass

def delete_elasticsearch(data):
  try:
    session = boto3.Session()
    credentials = session.get_credentials()

    awsauth = AWS4Auth(
      credentials.access_key,
      credentials.secret_key,
      session.region_name, "es",
      session_token=credentials.token
    )

    es = OpenSearch(
      [{"host": os.environ.get("OPENSEARCH_ENDPOINT"), "port": 443}],
      http_auth=awsauth,
      use_ssl=True,
      verify_certs=True,
      connection_class=RequestsHttpConnection
    )

    es.delete(
      index="products",
      id=data["id"],
      refresh=True
    )
  except Exception as e:
    # TODO: Figure out a better way to handle elasticsearch sync errors
    pass

def handler(event, context):
  for record in event["Records"]:
    if record["eventName"] in ["INSERT", "MODIFY"]:
      data = from_dynamodb_json({ "M": record["dynamodb"]["NewImage"]})
      index_elasticsearch(data)
    elif record["eventName"] == "REMOVE":
      data = from_dynamodb_json({ "M": record["dynamodb"]["OldImage"]})
      delete_elasticsearch(data)

  return {}
