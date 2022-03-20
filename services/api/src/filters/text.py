from opensearchpy import OpenSearch, RequestsHttpConnection
import traceback
import boto3
import os
from requests_aws4auth import AWS4Auth

from .filter import QueryFilter

class TextFilter(QueryFilter):
  es = None

  @staticmethod
  def initialize_open_search():
    if TextFilter.es != None:
      return

    session = boto3.Session()
    credentials =  session.get_credentials()

    awsauth = AWS4Auth(
      credentials.access_key,
      credentials.secret_key,
      session.region_name, "es",
      session_token= credentials.token
    )

    TextFilter.es = OpenSearch(
      [{"host": os.environ.get("OPENSEARCH_ENDPOINT"), "port": 443}],
      http_auth = awsauth,
      use_ssl = True,
      verify_certs = True,
      connection_class = RequestsHttpConnection
    )

  def __init__(self, config):
    TextFilter.initialize_open_search()

    self.config = config

  def query(self):
    try:
      products = []
      scores = []

      search_response = TextFilter.es.search(
        index="products",
        body={
          "query": {
            "match": {
              "label_text": {
                "query": self.config["text"],
                "fuzziness": "AUTO"  
              }
            }
          }
        }
      )

      for search_result in search_response["hits"]["hits"]:
        products.append(search_result["_source"])
        scores.append(search_result["_score"] / search_response["hits"]["max_score"])

      return products, scores
    except:
      traceback.print_exc()
      return [], []