from constructs import Construct
from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
)


class ApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, *, plotting_lambda, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Create REST API
        self.api = apigateway.RestApi(
            self,
            "PlottingApi",
            rest_api_name="Plotting Service",
        )

        # /plot resource
        plot_resource = self.api.root.add_resource("plot")

        # Lambda integration
        integration = apigateway.LambdaIntegration(plotting_lambda)

        plot_resource.add_method("GET", integration)
