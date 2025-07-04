# Force amd64 base image to ensure pip compatibility
FROM --platform=linux/amd64 python:3.10-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into container
COPY . .

# Optional: Silence GitPython warnings if applicable
ENV GIT_PYTHON_REFRESH=quiet

# Expose port and set entrypoint
EXPOSE 5000
CMD ["python", "resnet_classify.py"]
