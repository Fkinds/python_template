# ============================
# Stage 1: Builder
# ============================
FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential gcc git ca-certificates \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /build

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen

COPY . .

# ============================
# Stage 2: Runtime (rootless)
# ============================
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --gid 1000 dev \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash dev

WORKDIR /home/dev/app

COPY --from=builder /root/.local/bin/uv /usr/local/bin/uv
COPY --from=builder --chown=dev:dev /build/.venv /home/dev/app/.venv
COPY --from=builder --chown=dev:dev /build /home/dev/app

ENV PATH="/home/dev/app/.venv/bin:$PATH"

USER dev
EXPOSE 8000

ENTRYPOINT ["uv", "run"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
