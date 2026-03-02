# Step 1: Use a compatible Python version (3.10 is stable for pyATS)
FROM python:3.10-slim as builder

# Step 2: Install system dependencies required for pyATS and network connectivity
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libssl-dev \
    openssh-client \
    telnet \
    && rm -rf /var/lib/apt/lists/*

# Step 3: Set working directory and install Python dependencies
WORKDIR /app
COPY ../requirements.txt .
# Install pyATS[full] and other script requirements
RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt

# Step 4: Final Stage - Create a clean production image
FROM python:3.10-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    telnet \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Copy only the installed packages and your code from the builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY .. .

# Step 5: Ensure the backup directory exists inside the container
RUN mkdir -p /var/network-backups

# Step6: Ensure that the device backup script is executable
RUN chmod +x scripts/device_backup.py

# Default command to run your backup script
CMD ["python", "scripts/device_backup.py"]
