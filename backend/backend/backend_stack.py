from aws_cdk import (
    Stack,
    DockerImage,
    BundlingOptions,
    CfnOutput,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_wafv2 as waf
)
from constructs import Construct


class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # lambda function
        tap_backend_lambda = _lambda.Function(
            self, 'TapBackendLambda',
            code=_lambda.Code.from_asset(
                './lambda/',
                bundling=BundlingOptions(
                    image=DockerImage.from_registry('python:3.13'),
                    command=[
                        'bash', '-c',
                        'pip install -r requirements.txt --platform manylinux2014_x86_64 --only-binary=:all: -t /asset-output && cp -au . /asset-output',
                    ],
                )
            ),
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler='main.handler', # points to the app export in main.py
        )

        # api gateway
        api = apigw.LambdaRestApi(
            self,
            "TapAPIGateway",
            handler=tap_backend_lambda,
        )

        # Get API ID and Stage name
        api_id = api.rest_api_id
        stage_name = api.deployment_stage.stage_name

        # Construct the ARN in the format that WAF expects
        stage_arn = f"arn:aws:apigateway:{Stack.of(self).region}::/restapis/{api_id}/stages/{stage_name}"

        waf.CfnWebACLAssociation(self, "TapWAFAssociation",
            resource_arn=stage_arn,
            web_acl_arn="arn:aws:wafv2:us-west-2:812847476558:regional/webacl/waf-internal-20220921/55ac28c8-d996-4c20-9946-967d42b71601"
        )

        # output the api url
        CfnOutput(self, 'TapBackendApiUrl', value=api.url)




