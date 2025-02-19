import os
import json
import boto3
import tempfile

class ConfigManager:
    def __init__(self, secret_arn_env_var: str, local_config_path: str = None, region_name="us-west-2"):
        """
        Initialize the ConfigManager with the ARN of the secret.

        :param secret_arn_env_var: The environment variable name that contains the ARN of the secret.
        :param local_config_path: The path to the local configuration file.
        """
        self.secret_arn = os.getenv(secret_arn_env_var)
        self.local_config_path = local_config_path
        self.client = boto3.client('secretsmanager', region_name=region_name)

    def get_config(self) -> str:
        """
        Retrieve the secret from AWS Secrets Manager or the local configuration file.

        :return: The path to the configuration file.
        """
        # Try to retrieve the secret from AWS Secrets Manager
        if self.secret_arn:
            try:
                response = self.client.get_secret_value(SecretId=self.secret_arn)
                secret = response['SecretString']
                config_data = json.loads(secret)
                
                # Save the secret to a temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
                with open(temp_file.name, 'w') as f:
                    json.dump(config_data, f)
                return temp_file.name
            except self.client.exceptions.ClientError as e:
                print(f"Unable to retrieve secret: {e}")
        
        # Fallback: return the path to the local configuration file
        if self.local_config_path and os.path.exists(self.local_config_path):
            print("Local configuration file found.")
            return self.local_config_path
        else:
            raise FileNotFoundError("Local configuration file not found and unable to retrieve secret from AWS Secrets Manager.")