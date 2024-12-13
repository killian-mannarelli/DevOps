# Use a specific version of Python 3.9 with the slim image
FROM python:3.9.20-slim-bookworm

# Install necessary Python packages
RUN pip install google-cloud-bigquery kafka-python

# Prevent Python from buffering its output (for better log visibility in Docker)
ENV PYTHONUNBUFFERED=1

# Copy the BigQuery service account JSON file into the container
COPY ./service-account.json /app/service-account.json

# Copy the consumer application files into the container
COPY ./consumer/ /app/

# Set the working directory
WORKDIR /app

# Set environment variable for BigQuery authentication
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/service-account.json"

# Set the entrypoint command to run the consumer application
CMD ["python", "main.py"]
