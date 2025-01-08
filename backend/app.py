#!/usr/bin/env python3
import os

import aws_cdk as cdk

from backend.backend_stack import BackendStack


app = cdk.App()

cdk.Tags.of(app).add('org', 'tap')
cdk.Tags.of(app).add('billingId', '210125')

BackendStack(
    app,
    "TapBackendStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region="us-west-2"
    ),
)

app.synth()
