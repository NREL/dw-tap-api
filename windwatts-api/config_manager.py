import os
import json
import boto3

class ConfigManager:
    def __init__(self, secret_arn_env_var: str):
        """
        Initialize the ConfigManager with the ARN of the secret.

        :param secret_arn_env_var: The environment variable name that contains the ARN of the secret.
        """
        self.secret_arn = os.getenv(secret_arn_env_var)
        self.client = boto3.client('secretsmanager')

    def get_config(self):
        """
        Retrieve the secret from AWS Secrets Manager.

        :return: The secret as a dictionary.
        """
        try:
            response = self.client.get_secret_value(SecretId=self.secret_arn)
            secret = response['SecretString']
            return json.loads(secret)
        except self.client.exceptions.ClientError as e:
            print(f"Unable to retrieve secret: {e}")
            return None