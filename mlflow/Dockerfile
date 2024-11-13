# Dockerfile for MLflow
FROM python:3.8-slim

# Install MLflow and Google Cloud Storage library
RUN pip install mlflow google-cloud-storage psycopg2-binary

# Copy service account key to container
COPY ./gcp-nextloop.json /root/.gcp/gcp-nextloop.json

# Set proper permissions on the service account file
RUN chmod 700 /root/.gcp/gcp-nextloop.json 

# Set Google Application Credentials environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS="/root/.gcp/gcp-nextloop.json"

# Expose the MLflow default port
EXPOSE 5000

# Run MLflow server
CMD mlflow server \
    --backend-store-uri postgresql://postgres:postgres@34.64.231.49:5432/postgres \
    --default-artifact-root gs://dowhat-de1-mlfllowtest/mlflow-artifacts \
    --host 0.0.0.0 \
    --port 5000

