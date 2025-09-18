# sources/github_source.py
from pathlib import Path
from typing import List
from github import Github
from adapter import register_source
import base64, requests

@register_source("github")
class GithubSource:
    def __init__(self, token: str, repo_name: str, path: str = ""):
        self.repo = Github(token).get_repo(repo_name)
        self.path = path or ""   # root or subfolder

    def list_files(self) -> List[str]:
        items = self.repo.get_contents(self.path)
        return [it.path for it in items if it.type == "file"]

    def read_bytes(self, identifier: str) -> bytes:
        cf = self.repo.get_contents(identifier)

        if getattr(cf, "encoding", None) == "base64":
            return base64.b64decode(cf.content)

        if getattr(cf, "download_url", None):
            r = requests.get(cf.download_url, timeout=60)
            r.raise_for_status()
            return r.content

        raise RuntimeError(f"Cannot fetch file {identifier}")
