FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# برای psycopg و healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نصب وابستگی‌ها
COPY Werchaback/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# کپی کد
COPY Werchaback /app

# entrypoint
COPY Werchaback/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# healthcheck ساده
HEALTHCHECK --interval=30s --timeout=3s --retries=5 \
  CMD curl -fsS http://localhost:8000/healthz || exit 1

ENTRYPOINT ["/entrypoint.sh"]
