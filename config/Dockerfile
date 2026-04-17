# Stage 1: Build the Next.js static frontend
FROM node:24-slim AS frontend-build
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

# Stage 2: Python runtime serving FastAPI + the built frontend
FROM python:3.13-slim
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash friday \
    && mkdir -p /data /srv/frontend \
    && chown friday:friday /data /srv/frontend

USER friday
WORKDIR /home/friday/app

RUN python -m venv /home/friday/venv \
    && /home/friday/venv/bin/pip install --no-cache-dir \
        crewai \
        anthropic \
        openai \
        requests \
        fastapi \
        "uvicorn[standard]" \
        python-multipart

COPY --chown=friday:friday backend ./backend
COPY --chown=friday:friday pipeline ./pipeline
COPY --from=frontend-build --chown=friday:friday /build/out /srv/frontend

ENV PATH="/home/friday/venv/bin:$PATH"
ENV FRIDAY_DATA_DIR=/data
ENV FRIDAY_FRONTEND_DIR=/srv/frontend
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
