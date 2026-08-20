FROM python:3.12-slim


# =============================================================================
# Runtime environment
# =============================================================================

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ARTIFACTS_ROOT=/app/artifacts \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1


# =============================================================================
# Working directory
# =============================================================================

WORKDIR /app


# =============================================================================
# Frontend-only dependencies
# =============================================================================

COPY frontend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# =============================================================================
# Streamlit production configuration
# =============================================================================

COPY .streamlit ./.streamlit


# =============================================================================
# Frontend application
# =============================================================================

COPY frontend ./frontend


# =============================================================================
# Demonstration data required by Smart Analysis and Quick Demo
# =============================================================================

COPY data/interim/claims.parquet \
    ./data/interim/claims.parquet


# =============================================================================
# Lightweight frontend analytical artifacts
# =============================================================================

COPY artifacts/metadata \
    ./artifacts/metadata

COPY artifacts/explainability \
    ./artifacts/explainability


# =============================================================================
# Network
# =============================================================================

EXPOSE 8501


# =============================================================================
# Container health check
# =============================================================================

HEALTHCHECK \
    --interval=30s \
    --timeout=5s \
    --start-period=20s \
    --retries=3 \
    CMD python -c "import os, urllib.request; port = os.getenv('PORT', '8501'); urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health', timeout=3)" || exit 1


# =============================================================================
# Application startup
# =============================================================================

CMD ["sh", "-c", "streamlit run frontend/app.py --server.address=0.0.0.0 --server.port=${PORT:-8501} --server.headless=true --server.fileWatcherType=none"]