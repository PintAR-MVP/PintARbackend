"""
Data model for Products
"""
import boto3
import os
import datetime
import uuid

from common.utility.dynamodb import (
  to_dynamodb_json,
  from_dynamodb_json
)

PRODUCTS_TABLE_NAME = os.environ.get("PRODUCTS_TABLE_NAME")

class Products:
  def __init__(self, id: str = None, **kwargs):
    _data = { **kwargs, "id": id }
    
    if not id:
      _data["id"] = str(uuid.uuid4())
      _data["creation_date"] = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    # Directly access __dict__ to avoid infinite loop cause of overwritten __setattr__
    self.__dict__.update({
      "_data": _data,
      "_delete_flag": False
    })

  def __repr__(self):
    return f"Product(id={self.id})"

  def __getattr__(self, key):
    return self._data.get(key, None)

  def __setattr__(self, key, value):
    self._data[key] = value

  def __getitem__(self, key):
    return self._data.get(key, None)

  def __setitem__(self, key, value):
    self._data[key] = value

  def delete(self):
    # __setattr__ would be called otherwise
    self.__dict__["_delete_flag"] = True

  def commit(self):
    if self._delete_flag:
      try:
        dynamodb = boto3.client("dynamodb")
        dynamodb.delete_item(
          TableName=PRODUCTS_TABLE_NAME,
          Key={
            "id": to_dynamodb_json(self.id)
          }
        )
      except Exception as e:
        print(f"Cant delete product {str(self)} due to {str(e)}.")
        raise e
    else:
      exp_names = {}
      exp_values = {}
      exp_set = {}
      exp_remove = []

      for k, v in self._data.items():
        if k == "id":
          continue

        if v == None:
          exp_remove.append(f"#{k}")
          exp_names[f"#{k}"] = f"{k}"
        else:
          exp_set[f"#{k}"] = f":{k}"
          exp_names[f"#{k}"] = f"{k}"
          exp_values[f":{k}"] = v

      set_expression = ""
      for k, v in exp_set.items():
        if set_expression == "":
          set_expression = f"SET {k} = {v}"
        else:
          set_expression = f"{set_expression},{k} = {v}"

      remove_expression = f" REMOVE {','.join(exp_remove)}" if exp_remove else ""

      update_expression = set_expression + remove_expression

      try:
        dynamodb = boto3.client("dynamodb")
        dynamodb.update_item(
          TableName=PRODUCTS_TABLE_NAME,
          Key={"id": to_dynamodb_json(self.id)},
          UpdateExpression=update_expression,
          ExpressionAttributeValues={ k: to_dynamodb_json(v) for k, v in exp_values.items() },
          ExpressionAttributeNames=exp_names,
          ReturnValues="NONE"
        )
      except Exception as e:
        print(f"Cant update products {str(self)} due to {str(e)}.")
        raise e

  def as_dict(self, populated=False):
    if not populated:
      return self._data

    populated_dict = {}
    for k, v in self._data.items():
      populated_dict[k] = v
    return populated_dict

  @staticmethod
  def from_dict(inp):
    return Products(**inp)

  @staticmethod
  def get_by_id(id):
    try:
      dynamodb = boto3.client("dynamodb")
      product_dict = dynamodb.get_item(
        TableName=PRODUCTS_TABLE_NAME,
        Key={ "id": to_dynamodb_json(id) }
      )["Item"]

      return Products.from_dict({ k: from_dynamodb_json(v) for k, v in product_dict.items() })
    except Exception as e:
      print(f"Cant get product with id={id} due to {str(e)}.")
      raise e
