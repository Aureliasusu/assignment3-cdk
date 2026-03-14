from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
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
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ==============================
        # Plotting Lambda
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
        # REST API (plotting Lambda integration)
        # ==============================
        self.api = apigateway.RestApi(
            self,
            "PlottingApi",
            rest_api_name="Plotting Service",
        )
        plot_resource = self.api.root.add_resource("plot")
        plot_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(self.plotting_lambda),
        )
        # URL for GET /plot (no trailing slash)
        plot_api_url = self.api.url.rstrip("/") + "/plot"

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
            "PLOT_API_URL", plot_api_url
        )

        bucket.grant_read_write(self.driver_lambda)
