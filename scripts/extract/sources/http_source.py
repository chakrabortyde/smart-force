@register_source("http")
class HTTPSource:
    def __init__(self, urls: List[str]):
        self.urls = urls

    def list_files(self) -> List[str]:
        return self.urls  # identifiers are URLs

    def read_bytes(self, identifier: str) -> bytes:
        import requests
        r = requests.get(identifier, timeout=60)
        r.raise_for_status()
        return r.content
