import requests
import csv
import os
import click
import boto3
import random
import string

def temporary_username():
    random.seed(os.urandom(128))

    username = ""
    username += "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=20))
    username += "@example.com"

    return username

def temporary_password():
    random.seed(os.urandom(128))

    password = ""
    password += "".join(random.choices(string.ascii_uppercase, k=1))
    password += "".join(random.choices(string.ascii_lowercase, k=1))
    password += "".join(random.choices("0123456789", k=1))
    password += "".join(random.choices("#!?.,;:}{[]", k=1))
    password += "".join(random.choices(string.ascii_lowercase + string.ascii_uppercase + "0123456789" + "#!?.,;:}{[]", k=12))

    return password

@click.command()
@click.option("--access-key-id", required=True)
@click.option("--secret-access-key", required=True)
@click.option("--skip-images", flag_value=True)
def load_products(access_key_id=None, secret_access_key=None, skip_images=None):
    cloudformation = boto3.client("cloudformation",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    domain_name = None
    user_pool_id = None
    user_pool_client_id = None

    response = cloudformation.list_exports()
    for export in response["Exports"]:
        if export["Name"].startswith("pintar-api-domain-name-"):
            domain_name = export["Value"]
        elif export["Name"].startswith("pintar-api-cognito-user-pool-client-"):
            user_pool_client_id = export["Value"]
        elif export["Name"].startswith("pintar-api-cognito-user-pool-"):
            user_pool_id = export["Value"]

    username = temporary_username()
    password = temporary_password()

    cognito = boto3.client("cognito-idp",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    cognito.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        MessageAction="SUPPRESS"
    )

    cognito.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=username,
        Password=password,
        Permanent=True
    )

    response = cognito.admin_initiate_auth(
        UserPoolId=user_pool_id,
        ClientId=user_pool_client_id,
        AuthFlow="ADMIN_NO_SRP_AUTH",
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password
        }
    )
    access_token = response["AuthenticationResult"]["IdToken"]

    with open("../products/products.csv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)

        rows = [row for row in reader]

        count = 0
        total = len(rows)

        for row in rows:
            id, category, color, label_text, name, shape = row
            
            image_paths = []
            if skip_images != True:
                image_paths = [f"../products/{id}/{f}" for f in os.listdir(f"../products/{id}") if os.path.isfile(f"../products/{id}/{f}")]
            
            image_keys = []
            if len(image_paths) > 0:
                response = requests.post(f"{domain_name}/submit/product-image", 
                    headers={
                        "Authorization": access_token
                    },
                    json={
                        "count": len(image_paths)
                    }
                )
                response.raise_for_status()
                
                image_uploads = response.json()["images"]
                for image_path, image_upload in zip(image_paths, image_uploads):
                    image_upload_url = image_upload["upload_url"]

                    with open(image_path, "rb") as image_data:
                        response = requests.put(
                            image_upload_url,
                            headers={
                                "Content-Type": "image/jpeg"
                            },
                            data=image_data
                        )
                        response.raise_for_status()

                image_keys = [x["key"] for x in image_uploads]

            response = requests.post(f"{domain_name}/products",
                headers={
                    "Authorization": access_token
                },
                json={
                    "images": image_keys,
                    "name": name,
                    "label_text": label_text,
                    "shape": shape,
                    "color": color,
                    "category": category
                }
            )
            response.raise_for_status()
            
            count += 1
            print(f"{int((count / total) * 100.0)}%")
        print(f"Loaded {count} products.")

    cognito.admin_delete_user(
        UserPoolId=user_pool_id,
        Username=username
    )

if __name__ == "__main__":
    load_products()