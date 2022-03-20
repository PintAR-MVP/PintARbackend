from decimal import Decimal
from base64 import b64decode

def from_dynamodb_json(obj):
  assert isinstance(obj, dict)
  assert len(obj) == 1

  dynamodb_type = list(obj.keys())[0]
  dynamodb_value = obj[dynamodb_type]

  if dynamodb_type == "NULL":
    return None
  elif dynamodb_type == "BOOL":
    return dynamodb_value
  elif dynamodb_type == "N":
    decimal = Decimal(dynamodb_value)
    if decimal.as_integer_ratio()[1] == 1:
        return int(decimal)
    return float(decimal)
  elif dynamodb_type == "S":
    return dynamodb_value
  elif dynamodb_type == "B":
    if isinstance(dynamodb_value, str):
      return b64decode(dynamodb_value)
    elif isinstance(dynamodb_value, bytes):
      return dynamodb_value
    elif isinstance(dynamodb_value, bytearray):
      return bytes(dynamodb_value)
    else:
      assert False # Unknown type
  elif dynamodb_type == "L":
    result = []
    for v in dynamodb_value:
      result.append(from_dynamodb_json(v))
    return result
  elif dynamodb_type == "M":
    result = {}
    for k, v in dynamodb_value.items():
      result[k] = from_dynamodb_json(v)
    return result
  else:
    assert False # Unsupported type

def to_dynamodb_json(obj):
  if isinstance(obj, float) or isinstance(obj, int):
    return { "N": str(Decimal(str(obj))) }
  elif isinstance(obj, list):
    return { "L": [to_dynamodb_json(x) for x in obj] }
  elif isinstance(obj, dict):
    result = {}
    for key, value in obj.items():
      result[key] = to_dynamodb_json(value)
    return { "M": result }
  elif isinstance(obj, str):
    return { "S": obj }
  elif isinstance(obj, bool):
    return { "BOOL": obj }
  elif isinstance(obj, bytes):
    return { "B": obj }
  elif obj == None:
    return { "NULL": None }
  else:
    assert False # Unsupported type