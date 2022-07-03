import os
import secrets
import random
import boto3

s3 = boto3.client('s3',
                  aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))


def upload_file_to_s3(file, acl="public-read"):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(file.filename)
    picture_fn = random_hex + f_ext
    try:
        s3.upload_fileobj(
            file,
            os.environ.get('AWS_STORAGE_BUCKET_NAME'),
            picture_fn,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("Something Happened: ", e)
        return e
    return picture_fn
