import boto3
import botocore
import json
import hashlib
import binascii
import datetime

AWS_UPLOAD_MAX_SIZE = 20 * 1024 * 1024
AWS_UPLOAD_PART_SIZE = 6 * 1024 * 1024

def copy_s3(source_bucket, source_key, dest_bucket, dest_key):
  try:
    s3 = boto3.client("s3")
    s3.copy(
      CopySource={
        "Bucket": source_bucket,
        "Key": source_key
      },
      Bucket=dest_bucket,
      Key=dest_key
    )
  except Exception as e:
    print(f"Copy of object between s3 buckets failed due to {str(e)}.")
    raise e

def upload_to_s3(bucket, key, object, content_type):
  try:
    s3 = boto3.client("s3")
    s3.put_object(
      Bucket=bucket,
      Body=json.dumps(object),
      Key=key,
      ContentType=content_type
    )
  except Exception as e:
    print(f"Uploading of object to s3 bucket failed due to {str(e)}.")
    raise e

def download_from_s3(bucket, key):
  try:
    s3 = boto3.client("s3")
    response = s3.get_object(
      Bucket=bucket,
      Key=key
    )

    content_type = response["ContentType"]
    if content_type == "application/json":
      return json.load(response["Body"])
    
    return response["Body"].read()
  except Exception as e:
    print(f"Downloading of object from s3 bucket failed due to {str(e)}.")
    raise e

def delete_from_s3(bucket, key):
  try:
    s3 = boto3.client("s3")
    s3.delete_object(Bucket=bucket, Key=key)
  except Exception as e:
    print(f"Deletion of object from s3 failed due to {str(e)}.")
    raise e

def is_in_s3(bucket, key, object=None, max_age=None):
  metadata = _object_metadata_s3(bucket, key)

  if metadata and max_age:
    now = datetime.datetime.now(datetime.timezone.utc)
    last_modified = metadata["LastModified"]

    age = (now - last_modified).total_seconds()

    if age > max_age:
      return False
  elif metadata:
    pass
  else:
    return False

  if object:
    return _md5_s3(object) == metadata["ETag"][1:-1]

  return True

def create_presigned_url(bucket_name, object_name, operation="get_object", expiration=3600):
  try:
    s3 = boto3.client("s3")
    return s3.generate_presigned_url(
      operation,
      Params={
        "Bucket": bucket_name,
        "Key": object_name
      },
      ExpiresIn=expiration
    )
  except Exception as e:
    print(f"Can't create presigned url due to {str(e)}.")
    raise e

def _object_metadata_s3(bucket, key):
  try:
    s3 = boto3.client("s3")
    return s3.head_object(Bucket=bucket, Key=key)
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
      return None
    else:
      raise e

def _md5_s3(object):
  object_bytes = json.dumps(object).encode("utf8")

  if len(object_bytes) > AWS_UPLOAD_MAX_SIZE:
    block_count = 0
    md5string = ""
    for i in range(0, len(object_bytes), AWS_UPLOAD_PART_SIZE):
      hash = hashlib.md5()
      hash.update(object_bytes[i:i + AWS_UPLOAD_PART_SIZE])
      md5string = md5string + binascii.unhexlify(hash.hexdigest())
      block_count += 1

    hash = hashlib.md5()
    hash.update(md5string)
    return hash.hexdigest() + "-" + str(block_count)
  else:
    hash = hashlib.md5()
    for i in range(0, len(object_bytes), AWS_UPLOAD_PART_SIZE):
      hash.update(object_bytes[i:i + AWS_UPLOAD_PART_SIZE])
    return hash.hexdigest()