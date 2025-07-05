# foolbox-fgsm/Dockerfile
# Use slim Python base and enforce amd64 platform
FROM --platform=linux/amd64 python:3.10-slim

# Install system dependencies (only git needed here)
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files into container
COPY . .

# Silence GitPython warnings (safe to keep)
ENV GIT_PYTHON_REFRESH=quiet

# Expose Flask port and define default command
EXPOSE 5000
CMD ["python", "foolbox-fgsm.py"]
