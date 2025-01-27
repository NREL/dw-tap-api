import os
import json
import boto3

class ConfigManager:
    def __init__(self, secret_arn_env_var: str, local_config_path: str = None):
        """
        Initialize the ConfigManager with the ARN of the secret.

        :param secret_arn_env_var: The environment variable name that contains the ARN of the secret.
        :param local_config_path: The path to the local configuration file.
        """
        self.secret_arn = os.getenv(secret_arn_env_var)
        self.local_config_path = local_config_path
        self.client = boto3.client('secretsmanager')

    def get_config(self):
        """
        Retrieve the secret from AWS Secrets Manager.

        :return: The secret as a dictionary.
        """
        # Try to retrieve the secret from AWS Secrets Manager
        if self.secret_arn:
            try:
                response = self.client.get_secret_value(SecretId=self.secret_arn)
                secret = response['SecretString']
                return json.loads(secret)
            except self.client.exceptions.ClientError as e:
                print(f"Unable to retrieve secret: {e}")
        # fallback: try to retrieve the secret from the local configuration file
        try:
            with open(self.local_config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError as e:
            print(f"Local configuration file not found: {e}")
        return {}