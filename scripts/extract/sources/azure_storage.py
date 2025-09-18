from typing import List
from azure.storage.blob import ContainerClient
from adapter import register_source

@register_source("azure")
class AzureSource:
    def __init__(self, connection_string: str, container: str, prefix: str = ""):
        self.client = ContainerClient.from_connection_string(connection_string, container_name=container)
        self.prefix = prefix

    def list_files(self) -> List[str]:
        return [b.name for b in self.client.list_blobs(name_starts_with=self.prefix)]

    def read_bytes(self, identifier: str) -> bytes:
        return self.client.download_blob(identifier).readall()
