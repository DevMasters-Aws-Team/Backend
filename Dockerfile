FROM python:3.11-slim AS builder

WORKDIR /app
RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* README.md /app/
COPY kiro_agent/ /app/kiro_agent/

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

FROM python:3.11-slim AS runner
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . /app

EXPOSE 8080
CMD ["uvicorn", "kiro_agent.main:app", "--host", "0.0.0.0", "--port", "8080"]
