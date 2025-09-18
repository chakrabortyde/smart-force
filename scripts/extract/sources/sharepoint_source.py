from typing import List
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File
from adapter import register_source

@register_source("sharepoint")
class SharePointSource:
    def __init__(self, site_url: str, username: str, password: str, folder_path: str):
        self.ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))
        self.folder_path = folder_path

    def list_files(self) -> List[str]:
        folder = self.ctx.web.get_folder_by_server_relative_url(self.folder_path)
        self.ctx.load(folder.files); self.ctx.execute_query()
        return [f.properties["ServerRelativeUrl"] for f in folder.files]

    def read_bytes(self, identifier: str) -> bytes:
        result = File.open_binary(self.ctx, identifier)
        return result.content
