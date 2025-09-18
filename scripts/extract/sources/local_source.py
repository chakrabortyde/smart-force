from pathlib import Path
from typing import List
from adapter import register_source

@register_source("local")
class LocalSource:
    def __init__(self, raw_data_directory: str):
        self.root = Path(raw_data_directory)

    def list_files(self) -> List[str]:
        return [str(p.relative_to(self.root)) for p in self.root.glob("**/*") if p.is_file()]

    def read_bytes(self, identifier: str) -> bytes:
        return (self.root / identifier).read_bytes()
