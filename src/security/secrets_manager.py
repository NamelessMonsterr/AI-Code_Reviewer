import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SecretsManager:
    """Manage secrets securely"""

    def __init__(self, backend: str = "env"):
        """
        Initialize secrets manager

        Args:
            backend: 'env', 'aws', 'vault', 'gcp'
        """
        self.backend = backend
        self._cache = {}

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret value"""

        # Check cache first
        if key in self._cache:
            return self._cache[key]

        # Get from backend
        value = None

        if self.backend == "env":
            value = os.getenv(key, default)

        elif self.backend == "aws":
            value = self._get_from_aws(key, default)

        elif self.backend == "vault":
            value = self._get_from_vault(key, default)

        elif self.backend == "gcp":
            value = self._get_from_gcp(key, default)

        # Cache the value
        if value:
            self._cache[key] = value

        return value

    def _get_from_aws(self, key: str, default: Optional[str]) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""
        try:
            import boto3

            client = boto3.client("secretsmanager")
            response = client.get_secret_value(SecretId=key)
            return response["SecretString"]
        except Exception as e:
            logger.error(f"Failed to get secret from AWS: {e}")
            return default

    def _get_from_vault(self, key: str, default: Optional[str]) -> Optional[str]:
        """Get secret from HashiCorp Vault"""
        try:
            import hvac

            vault_url = os.getenv("VAULT_ADDR", "http://localhost:8200")
            vault_token = os.getenv("VAULT_TOKEN")

            client = hvac.Client(url=vault_url, token=vault_token)
            secret = client.secrets.kv.v2.read_secret_version(path=key)
            return secret["data"]["data"]["value"]
        except Exception as e:
            logger.error(f"Failed to get secret from Vault: {e}")
            return default

    def _get_from_gcp(self, key: str, default: Optional[str]) -> Optional[str]:
        """Get secret from GCP Secret Manager"""
        try:
            from google.cloud import secretmanager

            client = secretmanager.SecretManagerServiceClient()
            project_id = os.getenv("GCP_PROJECT_ID")
            name = f"projects/{project_id}/secrets/{key}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Failed to get secret from GCP: {e}")
            return default
