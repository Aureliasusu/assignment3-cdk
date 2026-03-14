#!/usr/bin/env python3
import aws_cdk as cdk

from assignment3_cdk.data_stack import DataStack
from assignment3_cdk.compute_stack import ComputeStack

app = cdk.App()

# Data: S3 bucket + DynamoDB table (with GSI)
data_stack = DataStack(app, "A3-DataStack")

# Compute: 3 lambdas + REST API (API URL passed to driver from same stack)
compute_stack = ComputeStack(
    app,
    "A3-ComputeStack",
    bucket=data_stack.bucket,
    table=data_stack.table,
)

app.synth()
