from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
)


class DataStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket
        self.bucket = s3.Bucket(
            self,
            "TestBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # DynamoDB table
        self.table = dynamodb.Table(
            self,
            "S3ObjectSizeHistory",
            partition_key=dynamodb.Attribute(
                name="bucket_name",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="ts",
                type=dynamodb.AttributeType.NUMBER,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.table.add_global_secondary_index(
            index_name="gsi_global_max",
            partition_key=dynamodb.Attribute(
                name="gsi_pk",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="total_size",
                type=dynamodb.AttributeType.NUMBER,
            ),
        )
