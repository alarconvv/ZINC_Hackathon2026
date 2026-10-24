FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /service
COPY backend/requirements.txt /service/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend /service/backend
COPY app /service/app
RUN useradd --uid 10001 --create-home zinc && chown -R zinc:zinc /service
USER zinc
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port \"${PORT:-8000}\" --no-access-log"]
