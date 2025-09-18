from pathlib import Path
import yaml

from sources import github_storage
from sinks import local_sink

from adapter import Adapter, build_source, build_sink

def main():
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)

        for cfg_snk in cfg["sinks"]:
            snk = build_sink(cfg_snk)
            for cfg_src in cfg["sources"]:
                src = build_source(cfg_src)

                adapter = Adapter(src, snk, preserve_paths=True)
                keys = adapter.run()
                print(f"Wrote {len(keys)} object(s):")
                for k in keys:
                    print(" -", k)

if __name__ == "__main__":
    main()
