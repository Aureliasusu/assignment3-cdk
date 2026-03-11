import boto3
import os
import time

REGION = os.environ["REGION"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
TABLE_NAME = os.environ["TABLE_NAME"]

s3 = boto3.client("s3", region_name=REGION)
ddb = boto3.resource("dynamodb", region_name=REGION)
table = ddb.Table(TABLE_NAME)


def calculate_bucket_size_and_count(bucket):
    total_size = 0
    total_count = 0

    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            total_size += obj["Size"]
            total_count += 1

    return total_size, total_count


def lambda_handler(event, context):
    """
    Triggered by S3 event.
    Record ONE snapshot only.
    """

    total_size, total_count = calculate_bucket_size_and_count(BUCKET_NAME)

    table.put_item(
        Item={
            "bucket_name": BUCKET_NAME,
            "ts": int(time.time()),
            "total_size": total_size,
            "object_count": total_count,
            "gsi_pk": "GLOBAL"
        }
    )

    return {"ok": True}
