# ============================
# Stage 1: Builder / CI
# ============================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential gcc git ca-certificates \
    && useradd --create-home --shell /bin/bash dev \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

WORKDIR /home/dev

# pyproject.toml と uv.lock をコピー
COPY pyproject.toml uv.lock* ./

# アプリをコピー
COPY . .

# Lint / 型チェック / テスト
RUN uv run ruff check .
RUN uv run mypy .
RUN uv run pytest --numprocesses auto # テストエラーでもビルド続行したい場合

# ============================
# Stage 2: Runtime
# ============================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl bash ca-certificates \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

RUN useradd --create-home --shell /bin/bash dev
WORKDIR /home/${USER}

# Builder ステージから仮想環境をコピー
COPY --from=builder /home/${USER}/.venv /home/${USER}/.venv
COPY --from=builder /home/${USER} /home/${USER}

ENV PATH="/home/dev/.venv/bin:$PATH"

# デフォルトで${USER}ユーザーで起動
USER ${USER}

COPY setEnv.sh /home/${USER}/setEnv.sh
RUN chmod +x /home/${USER}/setEnv.sh

CMD ["bash", "/home/${USER}/setEnv.sh"]
