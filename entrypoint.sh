#!/usr/bin/env bash
set -e

# اگر از Postgres استفاده می‌کنید، صبر کنید بالا بیاید (در سرور مفیده)
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database..."
  # اگر نام میزبان postgres باشد (در سرور)، این چک جواب می‌دهد؛ لوکال مشکلی نیست
  HOST=$(python - <<'PY'
import os, re
url=os.environ.get("DATABASE_URL","")
m=re.match(r'.*://.*@([^:/]+)', url)
print(m.group(1) if m else '')
PY
)
  if [ "$HOST" != "" ]; then
    until nc -z "$HOST" 5432; do sleep 1; done
  fi
fi

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# اجرای گونیکورن
exec gunicorn werchaapi.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 60
