import click
import boto3


@click.command()
@click.option("--access-key-id", required=True)
@click.option("--secret-access-key", required=True)
@click.option("--email", required=True)
@click.option("--password", required=True)
def create_user(access_key_id=None, secret_access_key=None, email=None, password=None):
    cloudformation = boto3.client("cloudformation",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    user_pool_id = None

    response = cloudformation.list_exports()
    for export in response["Exports"]:
        if export["Name"].startswith("pintar-api-domain-name-"):
            pass
        elif export["Name"].startswith("pintar-api-cognito-user-pool-client-"):
            pass
        elif export["Name"].startswith("pintar-api-cognito-user-pool-"):
            user_pool_id = export["Value"]

    cognito = boto3.client("cognito-idp",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    cognito.admin_create_user(
        UserPoolId=user_pool_id,
        Username=email,
        MessageAction="SUPPRESS"
    )

    cognito.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=email,
        Password=password,
        Permanent=True
    )

    print(f"Created user {email} with password {password}.")

if __name__ == "__main__":
    create_user()