# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements_mvp.txt /app/
RUN pip install --no-cache-dir -r requirements_mvp.txt

COPY pyproject.toml /app/
COPY src /app/src
COPY scripts/run_api.sh /app/scripts/run_api.sh
RUN chmod +x /app/scripts/run_api.sh

EXPOSE 8000
CMD ["uvicorn", "src.app.api_gateway:app", "--host", "0.0.0.0", "--port", "8000"]

