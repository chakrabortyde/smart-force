from pathlib import Path
import yaml

from sources import *
from sinks import *

from adapter import Adapter, build_source, build_sink

def main():
    cfg = yaml.safe_load(open("config.yaml"))
    src = build_source(cfg["source"])
    snk = build_sink(cfg["sink"])

    adapter = Adapter(src, snk, preserve_paths=True)
    keys = adapter.run()
    print(f"Wrote {len(keys)} object(s):")
    for k in keys:
        print(" -", k)

if __name__ == "__main__":
    main()
