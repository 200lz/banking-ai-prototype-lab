FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements-runtime.lock pyproject.toml ./
RUN pip install --no-cache-dir -r requirements-runtime.lock
COPY services ./services
COPY packages ./packages
COPY data ./data
RUN useradd --uid 10001 --create-home lab && mkdir -p /app/.runtime && chown -R lab:lab /app/.runtime
USER lab
EXPOSE 8000
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
