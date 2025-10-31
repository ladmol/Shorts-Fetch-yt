from __future__ import annotations

from pathlib import Path
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from .base import Storage


class S3Storage(Storage):
    def __init__(
        self,
        bucket: str,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        region: str = "us-east-1",
        addressing_style: str = "path",
        use_ssl: bool = False,
    ) -> None:
        s3_config = Config(s3={"addressing_style": addressing_style})
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            use_ssl=use_ssl,
            config=s3_config,
        )
        self.bucket = bucket
        self.region = region
        self._bucket_checked = False

    def _ensure_bucket(self) -> None:
        if self._bucket_checked:
            return
        try:
            self.client.head_bucket(Bucket=self.bucket)
            self._bucket_checked = True
            return
        except ClientError as e:
            error_code = int(e.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0))
            if error_code not in (404, 400):
                raise
        # Create bucket if missing
        try:
            if self.region and self.region != "us-east-1":
                self.client.create_bucket(
                    Bucket=self.bucket,
                    CreateBucketConfiguration={"LocationConstraint": self.region},
                )
            else:
                # For us-east-1, many S3-compatible backends require no configuration block
                self.client.create_bucket(Bucket=self.bucket)
        except ClientError as e:
            # Ignore if someone else just created it
            if e.response.get("Error", {}).get("Code") not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):  # type: ignore[truthy-bool]
                raise
        self._bucket_checked = True

    def save_bytes(self, relative_path: str, data: bytes) -> Path:
        self._ensure_bucket()
        self.client.put_object(Bucket=self.bucket, Key=relative_path, Body=data)
        # Return a pseudo-path for parity; actual location is S3 URL
        return Path(f"s3://{self.bucket}/{relative_path}")

    def upload_file(self, local_path: Path, key: str) -> str:
        self._ensure_bucket()
        self.client.upload_file(str(local_path), self.bucket, key)
        return f"s3://{self.bucket}/{key}"


