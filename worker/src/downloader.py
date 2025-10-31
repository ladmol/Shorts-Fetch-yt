from __future__ import annotations

from pathlib import Path
from typing import Optional

import yt_dlp


def download_video(url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Save as best mp4 if possible; fall back to best
    ydl_opts = {
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "noprogress": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Compute expected output path
        video_id = info.get("id")
        ext = info.get("ext", "mp4")
        file_path = out_dir / f"{video_id}.{ext}"
        if not file_path.exists():
            # Sometimes postprocessors change extension
            candidates = list(out_dir.glob(f"{video_id}.*"))
            if candidates:
                return candidates[0]
        return file_path


