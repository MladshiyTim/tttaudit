# TTT Audit sayti: Node vidjetlarni yigʻadi, Python Django'ni xizmat qiladi.
FROM node:24-alpine AS widgets
WORKDIR /w
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.14-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# Standart prod rejimi: settings.py dagi xavfsizlik bloki (HSTS, xavfsiz cookie,
# CompressedManifestStaticFilesStorage) yoqiladi. `docker run -e DJANGO_DEBUG=...`
# bilan qayta yozish mumkin, lekin buni hech qachon 1 ga qoʻymang (README: Prod: muhim).
ENV DJANGO_DEBUG=0
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=widgets /w/dist ./frontend/dist
# Statika build bosqichida yigʻiladi; bazasiz ishlashi uchun oʻrinbosar maxfiy kalit.
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput
# Root boʻlmagan foydalanuvchi; media/ (skanlar, suratlar, murojaat fayllari) unga yoziladigan boʻlsin
RUN useradd --create-home app && mkdir -p /app/media && chown -R app /app
USER app
# `exec` — gunicorn shell oʻrniga PID 1 boʻladi va SIGTERM'ni toʻgʻridan-toʻgʻri oladi
CMD sh -c "python manage.py migrate --noinput && \
           python manage.py createcachetable && \
           python manage.py seed_content && python manage.py import_tttaudit && \
           exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 --access-logfile -"
