# Force amd64 base image so pip installs compatible packages
FROM --platform=linux/amd64 python:3.10-slim

# Install git system dependency
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory and copy requirements
WORKDIR /app
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Silence GitPython warnings
ENV GIT_PYTHON_REFRESH=quiet

# Expose application port and launch
EXPOSE 5000
CMD ["python", "resnet_combined.py"]
