# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Bring in uv (pinned version) to install dependencies reproducibly.
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv

# Run as a non-root user: a container should never run as root without reason.
RUN useradd --create-home --uid 1000 ninca
WORKDIR /app

# Install only runtime dependencies, locked to uv.lock (supply-chain safe).
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
USER ninca
ENTRYPOINT ["ninca"]
CMD ["--help"]
