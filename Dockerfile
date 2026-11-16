FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/src ARTIFACTS_ROOT=/app/artifacts \
    PIP_NO_CACHE_DIR=1 APP_ENV=production \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
WORKDIR /app
COPY requirements/api.lock ./requirements/api.lock
RUN python -m pip install --require-hashes -r requirements/api.lock \
    && useradd --create-home --uid 10001 app
COPY api ./api
COPY src ./src
COPY configs ./configs
COPY artifacts/models ./artifacts/models
COPY artifacts/preprocessors ./artifacts/preprocessors
COPY artifacts/metadata/health_fraud_model_metadata.json ./artifacts/metadata/health_fraud_model_metadata.json
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8000')+'/health',timeout=3)" || exit 1
CMD ["sh", "-c", "exec python -m uvicorn api.app.main:app --host 0.0.0.0 --port=${PORT:-8000} --workers=1"]
