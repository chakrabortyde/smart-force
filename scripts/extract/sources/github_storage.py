from typing import List
from github import Github
from adapter import register_source

@register_source("github")
class GithubSource:
    def __init__(self, token: str, repo_name: str, path: str = ""):
        self.repo = Github(token).get_repo(repo_name)
        self.path = path

    def list_files(self) -> List[str]:
        queue = [self.path or ""]
        files: List[str] = []
        while queue:
            cur = queue.pop(0)
            for it in self.repo.get_contents(cur):
                if it.type == "dir":
                    queue.append(it.path)
                else:
                    files.append(it.path)
        return files

    def read_bytes(self, identifier: str) -> bytes:
        fc = self.repo.get_contents(identifier)
        return fc.decoded_content
