from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    Duration,
)
from constructs import Construct


class ComputeStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        bucket: s3.IBucket,
        table: dynamodb.ITable,
        plotting_api_url: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ==============================
        # Size Tracking Lambda
        # ==============================
        self.size_tracking_lambda = _lambda.Function(
            self,
            "SizeTrackingLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src/size_tracking"),
            timeout=Duration.seconds(60),
        )

        self.size_tracking_lambda.add_environment(
            "BUCKET_NAME", bucket.bucket_name
        )
        self.size_tracking_lambda.add_environment(
            "TABLE_NAME", table.table_name
        )
        self.size_tracking_lambda.add_environment(
            "REGION", self.region
        )

        bucket.grant_read(self.size_tracking_lambda)
        table.grant_write_data(self.size_tracking_lambda)

        # ==============================
        # Plotting Lambda  ⭐⭐⭐关键
        # ==============================
        self.plotting_lambda = _lambda.Function(
            self,
            "PlottingLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src/plotting"),
            timeout=Duration.seconds(60),
        )

        self.plotting_lambda.add_environment(
            "BUCKET_NAME", bucket.bucket_name
        )
        self.plotting_lambda.add_environment(
            "TABLE_NAME", table.table_name
        )
        self.plotting_lambda.add_environment(
            "REGION", self.region
        )

        bucket.grant_read_write(self.plotting_lambda)
        table.grant_read_data(self.plotting_lambda)

        # ==============================
        # Driver Lambda
        # ==============================
        self.driver_lambda = _lambda.Function(
            self,
            "DriverLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src/driver"),
            timeout=Duration.seconds(120),
        )

        self.driver_lambda.add_environment(
            "BUCKET_NAME", bucket.bucket_name
        )
        self.driver_lambda.add_environment(
            "REGION", self.region
        )
        self.driver_lambda.add_environment(
            "PLOT_API_URL", plotting_api_url
        )

        bucket.grant_read_write(self.driver_lambda)
