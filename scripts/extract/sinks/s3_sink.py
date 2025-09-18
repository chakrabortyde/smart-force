import boto3
from adapter import register_sink

@register_sink("s3")
class S3Sink:
    def __init__(self, bucket: str, prefix: str = ""):
        self.bucket = bucket
        self.prefix = prefix.rstrip("/")
        self.client = boto3.client("s3")

    def write_bytes(self, key: str, data: bytes) -> None:
        full_key = f"{self.prefix}/{key}" if self.prefix else key
        self.client.put_object(Bucket=self.bucket, Key=full_key, Body=data)
