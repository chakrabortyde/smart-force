from pathlib import Path
from typing import List, Protocol, Dict, Any, Type, Callable

class Source(Protocol):
    def list_files(self) -> List[str]: ...
    def read_bytes(self, identifier: str) -> bytes: ...

class Sink(Protocol):
    def write_bytes(self, key: str, data: bytes) -> None: ...

SOURCE_REGISTRY: Dict[str, Type] = {}
SINK_REGISTRY: Dict[str, Type] = {}

def register_source(name: str) -> Callable[[Type], Type]:
    def wrapper(cls: Type) -> Type:
        SOURCE_REGISTRY[name] = cls
        return cls
    return wrapper

def register_sink(name: str) -> Callable[[Type], Type]:
    def wrapper(cls: Type) -> Type:
        SINK_REGISTRY[name] = cls
        return cls
    return wrapper

def build_source(cfg: Dict[str, Any]) -> Source:
    typ = cfg["type"]
    cls = SOURCE_REGISTRY.get(typ)
    if not cls:
        raise ValueError(f"Unknown source type: {typ}. Registered: {list(SOURCE_REGISTRY.keys())}")
    return cls(**cfg.get("params", {}))

def build_sink(cfg: Dict[str, Any]) -> Sink:
    typ = cfg["type"]
    cls = SINK_REGISTRY.get(typ)
    if not cls:
        raise ValueError(f"Unknown sink type: {typ}. Registered: {list(SINK_REGISTRY.keys())}")
    return cls(**cfg.get("params", {}))

class Adapter:
    def __init__(self, source: Source, sink: Sink, preserve_paths: bool = False):
        self.source = source
        self.sink = sink
        self.preserve_paths = preserve_paths

    def run(self) -> List[str]:
        written: List[str] = []
        for file_id in self.source.list_files():
            data = self.source.read_bytes(file_id)
            key = file_id if self.preserve_paths else Path(file_id).name
            self.sink.write_bytes(key, data)
            written.append(key)
        return written
