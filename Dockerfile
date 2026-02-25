# Cosmic Origins sim server: serves web-viewer and runs gravity demos via API.
# Run with: docker compose up
FROM python:3.12-slim

WORKDIR /app

# Install dependencies (same as local dev)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy full repo so gravity module and tools resolve correctly
COPY . .

# Server runs from repo root; PYTHONPATH so "gravity" is importable from src
ENV PYTHONPATH=/app/src
ENV PORT=8000
EXPOSE 8000

# Run sim server (foreground); demo subprocess output streams to container logs
CMD ["python", "tools/sim_server.py"]
