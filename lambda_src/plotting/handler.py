import os
import json
import time
import boto3
from boto3.dynamodb.conditions import Key

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- env ----------
REGION = os.environ.get("AWS_REGION", "us-east-2")
BUCKET_NAME = os.environ["BUCKET_NAME"]
TABLE_NAME = os.environ["TABLE_NAME"]

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"

# ---------- aws clients ----------
s3 = boto3.client("s3", region_name=REGION)
ddb = boto3.resource("dynamodb", region_name=REGION)
table = ddb.Table(TABLE_NAME)

# ---------- queries ----------
def query_last_10_seconds(bucket):
    now = int(time.time())
    start = now - 10

    resp = table.query(
        KeyConditionExpression=
            Key("bucket_name").eq(bucket)
            & Key("ts").between(start, now),
        ScanIndexForward=True
    )

    return resp.get("Items", []), start


def query_global_max():
    resp = table.query(
        IndexName="gsi_global_max",
        KeyConditionExpression=Key("gsi_pk").eq("GLOBAL"),
        ScanIndexForward=False,
        Limit=1
    )

    items = resp.get("Items", [])
    return int(items[0]["total_size"]) if items else 0


# ---------- lambda ----------
def lambda_handler(event, context):

    print("Event:", event)

    items, start_ts = query_last_10_seconds(BUCKET_NAME)
    global_max = query_global_max()

    xs = [int(it["ts"]) - start_ts for it in items]
    ys = [int(it["total_size"]) for it in items]

    plt.figure(figsize=(8, 4))

    # main line
    if len(xs) >= 2:
        plt.plot(xs, ys, marker="o", linewidth=2,
                 label="Bucket size (last 10s)")
    elif len(xs) == 1:
        plt.scatter(xs, ys, s=60,
                    label="Bucket size (single point)")
    else:
        plt.text(5, 0.5, "No data in last 10 seconds",
                 ha="center", va="center")

    # historical max
    if global_max > 0:
        plt.axhline(
            global_max,
            linestyle="--",
            linewidth=2,
            label="Historical max"
        )

    # axis control
    all_vals = ys[:]
    if global_max > 0:
        all_vals.append(global_max)

    if all_vals:
        ymin = min(all_vals)
        ymax = max(all_vals)
        pad = max(10, int((ymax - ymin) * 0.2))
        plt.ylim(ymin - pad, ymax + pad)

    plt.xlim(0, 10)

    ax = plt.gca()
    ax.ticklabel_format(style="plain", axis="y", useOffset=False)

    plt.xlabel("Seconds (last 10 seconds)")
    plt.ylabel("Total size (bytes)")
    plt.title(f"S3 bucket size (last 10 seconds): {BUCKET_NAME}")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="upper right")

    # ---------- save ----------
    out_path = "/tmp/plot.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

    # ---------- upload ----------
    s3.upload_file(
        out_path,
        BUCKET_NAME,
        "plot",
        ExtraArgs={"ContentType": "image/png"}
    )

    print("Plot uploaded")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "ok": True,
            "points": len(xs),
            "global_max": global_max,
            "plot": f"s3://{BUCKET_NAME}/plot"
        })
    }
