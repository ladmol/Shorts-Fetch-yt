FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_SYSTEM_PYTHON=1

# Install curl + ffmpeg (alpine)
RUN apk add --no-cache curl ca-certificates ffmpeg

# Install uv (non-interactive)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Copy project config and source, then install via pyproject
COPY worker/pyproject.toml /app/pyproject.toml
COPY worker/src /app/src
RUN uv pip install --system -e .

# Create downloads dir
RUN mkdir -p /data/downloads
VOLUME ["/data/downloads"]

ENV DOWNLOADS_DIR=/data/downloads

CMD ["python", "-m", "src.main"]


