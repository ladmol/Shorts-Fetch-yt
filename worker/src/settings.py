from __future__ import annotations

import os
from pydantic import BaseModel


class Settings(BaseModel):
    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user: str = os.getenv("RABBITMQ_USER", os.getenv("RABBITMQ_DEFAULT_USER", "guest"))
    rabbitmq_pass: str = os.getenv("RABBITMQ_PASS", os.getenv("RABBITMQ_DEFAULT_PASS", "guest"))
    rabbitmq_queue: str = os.getenv("RABBITMQ_QUEUE", "download.tasks")
    results_queue: str = os.getenv("RESULTS_QUEUE", "download.results")

    downloads_dir: str = os.getenv("DOWNLOADS_DIR", "/data/downloads")

    # S3 / MinIO
    s3_endpoint: str = os.getenv("S3_ENDPOINT_URL", os.getenv("MINIO_ENDPOINT", "http://minio:9000"))
    s3_access_key: str = os.getenv("AWS_ACCESS_KEY_ID", os.getenv("MINIO_ROOT_USER", "minioadmin"))
    s3_secret_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"))
    s3_region: str = os.getenv("AWS_REGION", "us-east-1")
    s3_bucket: str = os.getenv("S3_BUCKET", os.getenv("MINIO_BUCKET", "downloads"))
    s3_addressing_style: str = os.getenv("S3_ADDRESSING_STYLE", "path")


settings = Settings()


