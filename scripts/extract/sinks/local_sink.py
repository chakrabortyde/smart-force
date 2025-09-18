from pathlib import Path
from adapter import register_sink

@register_sink("local")
class LocalSink:
    def __init__(self, base_dir: str = "./out"):
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def write_bytes(self, key: str, data: bytes) -> None:
        p = self.base / key
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
