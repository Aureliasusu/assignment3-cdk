from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
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

        # Size-tracking Lambda (same stack as bucket to avoid circular dependency)
        self.size_tracking_lambda = _lambda.Function(
            self,
            "SizeTrackingLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src/size_tracking"),
            timeout=Duration.seconds(60),
        )
        self.size_tracking_lambda.add_environment("BUCKET_NAME", self.bucket.bucket_name)
        self.size_tracking_lambda.add_environment("TABLE_NAME", self.table.table_name)
        self.size_tracking_lambda.add_environment("REGION", self.region)
        self.bucket.grant_read(self.size_tracking_lambda)
        self.table.grant_write_data(self.size_tracking_lambda)

        # S3 event: bucket -> size-tracking lambda (OBJECT_CREATED)
        self.bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(self.size_tracking_lambda),
        )
