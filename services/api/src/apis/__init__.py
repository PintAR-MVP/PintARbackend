from flask_restx import Api

from .products import api as ProductsApi
from .search import api as SearchApi
from .submit import api as SubmitApi

import traceback

api = Api(
  title="PintAR API",
  version="1.0",
  description="API for PintAR IOS app and the PintAR import tool."
)

@api.errorhandler(Exception)
def error_handler(error):
  return {
    "status": "Internal Server Error",
    "code": 500,
    "message": "During request handling an unhandled exception occured.",
    "description": {
      "exception": f"{error}",
      "exception_type": f"{type(error)}",
      "traceback": traceback.format_exc()
    }
  }, 500

api.add_namespace(ProductsApi, path="/products")
api.add_namespace(SearchApi, path="/search")
api.add_namespace(SubmitApi, path="/submit")