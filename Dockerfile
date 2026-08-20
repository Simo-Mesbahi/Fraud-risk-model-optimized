FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/src \
    ARTIFACTS_ROOT=/app/artifacts \
    PIP_NO_CACHE_DIR=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1


WORKDIR /app


# API and model-inference dependencies only
COPY api/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


COPY api ./api
COPY src ./src


COPY artifacts/models \
    ./artifacts/models

COPY artifacts/preprocessors \
    ./artifacts/preprocessors

COPY artifacts/metadata/health_fraud_model_metadata.json \
    ./artifacts/metadata/health_fraud_model_metadata.json


EXPOSE 8000


HEALTHCHECK \
    --interval=30s \
    --timeout=5s \
    --start-period=20s \
    --retries=3 \
    CMD python -c "import os, urllib.request; port = os.getenv('PORT', '8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=3)" || exit

CMD ["sh", "-c", "python -m uvicorn api.app.main:app --host 0.0.0.0 --port=${PORT:-8000} --workers=1"]