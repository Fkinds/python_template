# ============================
# Stage 1: Builder / CI
# ============================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential gcc git \
    && useradd --create-home --shell /bin/bash dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install pipx \
    && pipx ensurepath \
    && pipx install uv \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:/root/.local/pipx/venvs/uv/bin:$PATH"

WORKDIR /home/dev

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry export --without-hashes --only main,dev --format=requirements.txt -o requirements.txt \
    && uv pip install --system -r requirements.txt \
    && rm requirements.txt

# COPY app/ /home/dev/app
# COPY tests/ /home/dev/tests

# # Lint / 型チェック / テスト
# RUN ruff check app tests && \
#     mypy app && \
#     pytest tests

# ============================
# Stage 2: Runtime
# ============================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    pipx curl bash util-linux \
    && pipx ensurepath \
    && pipx install uv \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:/root/.local/pipx/venvs/uv/bin:$PATH"

RUN useradd --create-home --shell /bin/bash dev

WORKDIR /home/${USER}

COPY --chown=dev:dev --from=builder /home/${USER} /home/${USER}
COPY setEnv.sh /home/${USER}/setEnv.sh
RUN chmod +x /home/${USER}/setEnv.sh

# デフォルトで${USER}ユーザーで起動
USER ${USER}

CMD ["bash", "/home/${USER}/setEnv.sh"]
