FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /service/mobileApp
COPY mobileApp/backend/requirements.txt /service/mobileApp/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY mobileApp/backend /service/mobileApp/backend
COPY mobileApp/core /service/mobileApp/core
RUN useradd --uid 10001 --create-home zinc && chown -R zinc:zinc /service
USER zinc
EXPOSE 8000
# With DEMO_PASSWORD set, create the fictional demo account first; the seeder never overwrites an existing one.
CMD ["sh", "-c", "if [ -n \"$DEMO_PASSWORD\" ]; then python -m backend.seed_demo; fi; exec uvicorn backend.main:app --host 0.0.0.0 --port \"${PORT:-8000}\" --no-access-log"]
