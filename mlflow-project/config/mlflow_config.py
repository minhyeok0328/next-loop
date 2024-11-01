import os
from dotenv import load_dotenv

load_dotenv()

# MLflow 환경 설정
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI')
MLFLOW_S3_ENDPOINT_URL = os.getenv('MLFLOW_S3_ENDPOINT_URL')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
MLFLOW_S3_IGNORE_TLS = os.getenv('MLFLOW_S3_IGNORE_TLS')
MLFLOW_HTTP_REQUEST_TIMEOUT = os.getenv('MLFLOW_HTTP_REQUEST_TIMEOUT')

EXTERNAL_IP = "34.64.68.155"  #외부IP변경 GCP Instance

# MLflow 설정
EXPERIMENT_NAME = "pytorch_example"
MODEL_NAME = "simple_model"

# Training parameters
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001

# Model parameters
INPUT_SIZE = 10
HIDDEN_SIZE = 64
OUTPUT_SIZE = 1
