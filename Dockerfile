# ============================
# Stage 1: Builder / CI
# ============================
FROM python:3.14.0-slim AS builder

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

# uv を実行して依存関係を同期
RUN uv sync --frozen

# Lint / 型チェック / テスト
RUN uv run ruff check .
RUN uv run mypy .
RUN uv run pytest --numprocesses auto # テストエラーでもビルド続行したい場合

# ============================
# Stage 2: Runtime
# ============================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl bash ca-certificates \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /home/dev

# Python 仮想環境を作る
RUN python3 -m venv .venv
ENV PATH="/home/dev/.venv/bin:$PATH"

# uv のローカル環境を使う場合はここで uv install または uv sync
COPY pyproject.toml uv.lock* ./

# アプリ本体をコピー
COPY --from=builder /home/dev ./

RUN uv sync --frozen

# Postgres ドライバを追加
RUN pip install --no-cache-dir "psycopg[binary]"

RUN useradd --create-home --shell /bin/bash dev

# デフォルトで${USER}ユーザーで起動
USER dev
EXPOSE 8000

# Django サーバーを起動
CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
