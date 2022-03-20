# backend"# PintARbackend" 

# Deployment instructions

## Install third party software
1. Follow the instructions at https://nodejs.org/en/download/ to install a recent version of nodejs and npm (NOTE: tested with nodejs v14.18.1 and npm 6.14.15)
2. Follow the instructions at https://www.serverless.com/framework/docs/getting-started to install the serverless framework (NOTE: tested with Framework Core 2.69.1, Plugin 5.5.1, SDK 4.3.0 and Components 3.18.1)
3. Follow the instructions at https://www.python.org/downloads/ to install a recent version of python (NOTE: tested with python 3.8.10)
4. If you are using windows, please follow the instructions at https://docs.docker.com/desktop/windows/install/ to install a recent version of docker (NOTE: tested with docker 20.10.11)

## Setup AWS
1. Import your domain into AWS Route53. Step-by-step instructions for that can be found at https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/migrate-dns-domain-in-use.html. (NOTE: The domain name will be referred to as “DOMAIN”)
2. Look up the hosted zone id of the domain you just imported. (NOTE: The hosted zone id will be referred to as “HOSTED_ZONE_ID”)
3. Create a IAM user for the deployment. For the AWS credential type choose “Access key -Programmatic access”. (NOTE: The access key id and secret access key will be referred to as “ACCESS_KEY_ID” and “SECRET_ACCESS_KEY”)
4. Create and attach a IAM policy with the required permissions to the newly created user. A policy document containing the required permissions can be found in APPENDIX 1 and step-by-step instructions for the creation and attachment of this policy can be found at https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-and-attach-iam-policy.html.

## Download the code
1. Download the source code from … and extract it to an empty directory (NOTE: This directory will be referred to as “PROJECT_DIR”)

## Deploy the API
1. Choose a subdomain under which you would like to make the API accessible. (Note: This subdomain will be referred to as “API_SUBDOMAIN”)
2. Create an SSL certificate for “API_SUBDOMAIN.DOMAIN” in the AWS certificate manager. Make sure you create the certificate in the “eu-west-1” region. Step-by-step instructions for that can be found at https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html. 
3. Look up the ARN of the SSL certificate you just created. (NOTE: The ARN will be referred to as “API_CERTIFICATE_ARN”)
4. Modify the file “PROJECT_DIR/services/api/serverless.yml”
  - In Line 129 replace “api.pint-ar.de” with “API_SUBDOMAIN.DOMAIN”
  -	In Line 131 replace “arn:aws:acm:eu-central-1:235501516910:certificate/67ec2276-cc0c-427b-9e17-7e37f1595233” with “API_CERTIFICATE_ARN”
  - In Line 135 replace “Z06771035RYK5PGM23RO“ with “HOSTED_ZONE_ID”
5. Open a console and run the following commands
  - cd PROJECT_DIR/services/api
  - npm install
  - serverless config credentials --provider aws --key ACCESS_KEY_ID --secret SECRET_ACCESS_KEY
  - serverless deploy --stage prod

## (Optional) Load test products into the product database:
1. Open a console and run the following commands
  - cd PROJECT_DIR/scripts
  - pip3 install -r requirements.txt
  - python3 load_products.py --access-key-id ACCESS_KEY_ID --secret-access-key SECRET_ACCESS_KEY --skip-images

## (Optional) Create admin credentials:
1. Choose an email and a password. The password must be at least 8 characters long and needs to contain at least one special character and at least one number. (Note: The email and password will be referred to as “EMAIL” and “PASSWORD”)
2. Open a console and run the following commands
  - cd PROJECT_DIR/scripts
  - pip3 install -r requirements.txt
  - python3 create_user.py --access-key-id ACCESS_KEY_ID --secret-access-key SECRET_ACCESS_KEY --email EMAIL --password PASSWORD

## (Optional) Deploy the import tool:
1. Choose a subdomain under which you would like to make the Product import tool accessible. (Note: This subdomain will be referred to as “UI_SUBDOMAIN”)
2. Create an SSL certificate for “UI_SUBDOMAIN.DOMAIN” in the AWS certificate manager. Make sure you create the certificate in the “us-east-1” region. Step-by-step instructions for that can be found at https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html. 
3. Look up the ARN of the SSL certificate you just created. (NOTE: The ARN will be referred to as “UI_CERTIFICATE_ARN”)
4. Modify the file “PROJECT_DIR/services/ui/serverless.yml”
  - In Line 49 replace “ui.pint-ar.de” with “UI_SUBDOMAIN.DOMAIN”
  - In Line 51 replace “arn:aws:acm:us-east-1:235501516910:certificate/e1703dca-38ea-40a8-bbc9-118c11bda693” with “UI_CERTIFICATE_ARN”
  - In Line 55 replace “Z06771035RYK5PGM23RO“ with “HOSTED_ZONE_ID”
5. Open a console and run the following commands
  - cd PROJECT_DIR/services/ui
  - npm install
  - serverless config credentials --provider aws --key ACCESS_KEY_ID --secret SECRET_ACCESS_KEY
  - serverless deploy --stage prod

# Import tool

The import tool allows admins to load new products into the database. To load a product into the database:

1. Complete all steps (including the optional steps) of the deployment instructions.
2. Open the browser and navigate to the import tool’s domain you choose during deployment.
3. Enter the admin credentials you choose during deployment and click on “SIGN IN”.
4. Submit the product:
  - Choose one or multiple images of the product, you can open the selection dialog by clicking on “Select”.
  - Finish the submission by clicking on “Upload”.
5. Start the validation process:
  - Navigate to the Validation-View by clicking on “Submission Validation”.
  - Click on “Refresh” to start the validation process.
6. Ensure that all form fields contain the correct value.
  - The “Name” field should contain the name of the product.
  - The “Category” field should contain the category of the product.
  - The “Label Text” field should contain all text that is written on the product label.
  - The “Shape” field should contain the WKT representation of a polygon describing the outline of the product. To fill that field, you should follow these steps:
    -	Click on “Draw Shape”.
    - Draw the outline of the product by left clicking on the product image.
    - Click on “Save Shape”.
  - The “Color” field should contain the average color of the product. To fill that field, you should follow these steps:
    - Click on “Save Color”.
7. Complete the validation process by clicking on “Create Product”.
