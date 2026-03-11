import boto3
import time
import urllib.request
import urllib.error
import ssl
import os

REGION = os.environ["REGION"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
PLOT_API_URL = os.environ["PLOT_API_URL"]

s3 = boto3.client("s3", region_name=REGION)


def call_plot_api():
    print("Calling plotting API:", PLOT_API_URL)

    req = urllib.request.Request(
        PLOT_API_URL,
        method="GET",
        headers={
            "User-Agent": "lambda-driver",
            "Accept": "application/json"
        },
    )

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            print("Plot API response:", body)
            return body

    except urllib.error.HTTPError as e:
        print("HTTP ERROR:", e.code, e.read().decode())
        raise

    except Exception as e:
        print("CALL FAILED:", str(e))
        raise


def lambda_handler(event, context):

    for i in range(5):
        key = f"assignment_step_{i}.txt"
        body = b"a" * (5000 * (i + 1))

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=body,
        )

        print("Created", key)
        time.sleep(1)

    for i in range(3):
        key = f"assignment_step_{i}.txt"

        s3.delete_object(
            Bucket=BUCKET_NAME,
            Key=key,
        )

        print("Deleted", key)
        time.sleep(1)

    result = call_plot_api()

    return {
        "ok": True,
        "api_response": result,
    }
