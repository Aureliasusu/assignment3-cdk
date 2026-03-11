#!/usr/bin/env python3
import aws_cdk as cdk

from assignment3_cdk.data_stack import DataStack
from assignment3_cdk.compute_stack import ComputeStack
from assignment3_cdk.api_stack import ApiStack

app = cdk.App()

# Data
data_stack = DataStack(app, "A3-DataStack")

# Compute (NO API dependency)
compute_stack = ComputeStack(
    app,
    "A3-ComputeStack",
    bucket=data_stack.bucket,
    table=data_stack.table,
    plotting_api_url="https://lhml6eu8m7.execute-api.us-east-2.amazonaws.com/prod/plot",
)

# API
api_stack = ApiStack(
    app,
    "A3-ApiStack",
    plotting_lambda=compute_stack.plotting_lambda,
)

app.synth()
