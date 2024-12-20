from aws_cdk import (
    Duration,
    Stack,
    BundlingOptions,
    CfnOutput,
    aws_lambda as _lambda,
    aws_iam as iam,
)
from constructs import Construct

from aws_cdk.aws_apigatewayv2 import (
    HttpMethod,
    HttpApi,
    CorsPreflightOptions,
    CorsHttpMethod
)
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration

class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # iam role for lambda
        lambda_role = iam.Role(
            self, 'TapBackendLambdaExecutionRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
            ],
        )

        # lambda function
        tap_backend_lambda = _lambda.Function(
            self, 'TapBackendLambda',
            code=_lambda.Code.from_asset(
                './lambda/',
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_8.bundling_image,
                    command=[
                        'bash', '-c',
                        'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output',
                    ],
                )
            ),
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='main.handler', # points to the app export in main.py
            architecture=_lambda.Architecture.ARM_64,
            role=lambda_role,
            memory_size=128,
            timeout=Duration.seconds(29),
        )

        # api gateway
        http_api = HttpApi(
            self, 'TapBackendApiGateway',
            cors_preflight=CorsPreflightOptions(
                allow_headers=["Authorization", "Content-Type"],
                allow_origins=['*'],
                allow_methods=[
                    CorsHttpMethod.GET,
                    CorsHttpMethod.OPTIONS,
                    CorsHttpMethod.HEAD,
                ],
                max_age=Duration.days(10),
            ),
        )

        # api gateway integration with proxy routes
        http_api.add_routes(
            path="/{proxy+}",
            methods=[HttpMethod.ANY],
            integration=HttpLambdaIntegration(
                "TapBackendLambdaIntegration",
                handler=tap_backend_lambda,
            ),
        )

        # output the api url
        CfnOutput(self, 'TapBackendApiUrl', value=http_api.url)




