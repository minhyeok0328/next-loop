# Dockerfile for MLflow
FROM python:3.8-slim

# Install MLflow and Google Cloud Storage library
RUN pip install mlflow google-cloud-storage psycopg2-binary

# Copy service account key to container
COPY ./${GOOGLE_APPLICATION_CREDENTIALS} /root/.gcp/${GOOGLE_APPLICATION_CREDENTIALS}

# Set proper permissions on the service account file
RUN chmod 600 /root/.gcp/${GOOGLE_APPLICATION_CREDENTIALS} 

# Set Google Application Credentials environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS="/root/.gcp/${GOOGLE_APPLICATION_CREDENTIALS}"

# Expose the MLflow default port
EXPOSE 5000

# Run MLflow server
CMD mlflow server \
    --backend-store-uri ${backend-store-uri} \
    --default-artifact-root ${artifact-root} \
    --host 0.0.0.0 \
    --port 5000

