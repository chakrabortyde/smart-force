import boto3
from typing import List
from adapter import register_source

@register_source("s3")
class S3Source:
    def __init__(self, bucket: str, prefix: str = ""):
        self.bucket = bucket
        self.prefix = prefix
        self.client = boto3.client("s3")

    def list_files(self) -> List[str]:
        keys: List[str] = []
        token = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": self.prefix}
            if token: kwargs["ContinuationToken"] = token
            resp = self.client.list_objects_v2(**kwargs)
            for obj in resp.get("Contents", []):
                keys.append(obj["Key"])
            if not resp.get("IsTruncated"):
                break
            token = resp.get("NextContinuationToken")
        return keys

    def read_bytes(self, identifier: str) -> bytes:
        obj = self.client.get_object(Bucket=self.bucket, Key=identifier)
        return obj["Body"].read()
