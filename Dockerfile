FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN addgroup --system app
RUN adduser --ingroup app app_user

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Add only what's needed
COPY README.md ./README.md
COPY main.py ./main.py
COPY entrypoint.sh ./entrypoint.sh

RUN chown -R app_user:app /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv sync --locked --no-dev --no-cache

EXPOSE 8000

USER app_user

ENTRYPOINT ["/app/entrypoint.sh"]
