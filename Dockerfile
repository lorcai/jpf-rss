# ---- Base image ----
FROM python:3.11-slim

# ---- Environment hygiene ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Madrid

# ---- System dependencies ----
# Needed for:
# - lxml
# - timezone correctness
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /app

# ---- Python dependencies ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Project files ----
COPY src/ src/
COPY data/ data/
COPY docs/ docs/

# Ensure directories exist even on first run
RUN mkdir -p data docs

# ---- Default command ----
# Runs the full pipeline
CMD ["python", "src/pipeline.py"]

