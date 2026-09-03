FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

# pyproject.toml이 ai-common을 ../ai-common(로컬 편집 가능 경로)로 참조하므로,
# Render처럼 이 레포 하나만 clone하는 환경에서도 같은 상위 디렉토리 구조를 재현해줘야 함.
WORKDIR /build
RUN git clone --depth 1 https://github.com/2026-AI-Challenge-swu/ai-common.git ai-common

COPY . /build/ai-agent-core
WORKDIR /build/ai-agent-core

RUN uv sync --no-dev

EXPOSE 8000

CMD ["sh", "-c", "uv run uvicorn src.ai_agent_core.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
