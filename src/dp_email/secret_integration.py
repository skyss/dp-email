"""Integration with Azure Key Vault Secrets."""

from azure.identity import DefaultAzureCredential  # type: ignore [import]
from azure.keyvault.secrets import SecretClient  # type: ignore [import]


def get_secret(vault_url: str, secret_name: str) -> str:
    """Retrieve a secret value from Azure Key Vault.

    Args:
    ----
        vault_url (str): Key vault url to get secret from
        secret_name (str): Name of the secret

    Returns:
    -------
        str: Value of the secret

    """
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    result = client.get_secret(secret_name)
    return str(result.value)
