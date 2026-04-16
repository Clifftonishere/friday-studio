FROM ghcr.io/openclaw/openclaw:latest

USER root

# Install system deps
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps in venv
RUN python3 -m venv /home/node/crewai-env \
    && /home/node/crewai-env/bin/pip install --no-cache-dir \
        crewai \
        anthropic \
        openai \
        requests \
        fastapi \
        "uvicorn[standard]" \
        python-multipart \
    && chown -R node:node /home/node/crewai-env

# Build Next.js frontend as static export
COPY frontend /tmp/frontend
RUN cd /tmp/frontend && npm ci && npm run build \
    && mv /tmp/frontend/out /home/node/frontend-static \
    && rm -rf /tmp/frontend \
    && chown -R node:node /home/node/frontend-static

# Copy backend + pipeline code
COPY backend /home/node/app/backend
COPY pipeline /home/node/app/pipeline
RUN chown -R node:node /home/node/app

# Create data directory
RUN mkdir -p /data && chown node:node /data

USER node

# Start FastAPI
WORKDIR /home/node/app
ENV PATH="/home/node/crewai-env/bin:$PATH"
ENV FRIDAY_DATA_DIR="/data"
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
