from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from .consumer import MessageContext, consume
from .settings import settings
from .publisher import publish
from .downloader import download_video
from .storage.s3 import S3Storage


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def handle_message(ctx: MessageContext) -> None:
    try:
        payload = json.loads(ctx.body.decode("utf-8"))
    except json.JSONDecodeError:
        payload = {"raw": ctx.body.decode("utf-8", errors="ignore")}

    task_id = str(payload.get("id") or payload.get("task_id") or "task")
    url = payload.get("url")
    attempts = int(payload.get("attempts", 0))

    if not url:
        logger.error("No URL provided in payload: %s", payload)
        return

    try:
        # 1) Download video to local tmp dir under downloads_dir/tmp
        tmp_dir = Path(settings.downloads_dir) / "tmp" / task_id
        local_file = download_video(url, tmp_dir)

        # 2) Upload to S3/MinIO
        s3 = S3Storage(
            bucket=settings.s3_bucket,
            endpoint_url=settings.s3_endpoint,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            region=settings.s3_region,
            addressing_style=settings.s3_addressing_style,
            use_ssl=settings.s3_endpoint.startswith("https://"),
        )
        key = f"{task_id}/{local_file.name}"
        s3_url = s3.upload_file(local_file, key)
        logger.info("Uploaded to S3: %s", s3_url)

        # 3) Publish result
        result_payload = {
            "id": task_id,
            "url": url,
            "s3_url": s3_url,
            "bucket": settings.s3_bucket,
            "key": key,
            "status": "success",
        }
        publish(settings.results_queue, result_payload)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Task failed: %s", exc)
        if attempts < int(os.getenv("MAX_ATTEMPTS", "3")):
            retry_payload = dict(payload)
            retry_payload["attempts"] = attempts + 1
            publish(settings.rabbitmq_queue, retry_payload)
            logger.info("Requeued task %s with attempts=%s", task_id, attempts + 1)
        else:
            publish(settings.results_queue, {"id": task_id, "url": url, "status": "failed", "error": str(exc)})


def main() -> None:
    Path(settings.downloads_dir).mkdir(parents=True, exist_ok=True)
    consume(handle_message)


if __name__ == "__main__":
    main()


