### config/mlflow_config.py ###
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

#MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI') : 기존
MLFLOW_TRACKING_URI = "http://localhost:5000" # Local : 기존 PostgreSQL URI 대신 MLflow 서버 주소 사용

EXPERIMENT_NAME = "pytorch_example"
MODEL_NAME = "simple_model"

# Local
# MinIO 설정
os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://localhost:9000"  # MinIO 주소
os.environ['AWS_ACCESS_KEY_ID'] = "minio"                       # MinIO 접근 키
os.environ['AWS_SECRET_ACCESS_KEY'] = "minio123"                # MinIO 비밀 키

# Training parameters
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001

# Model parameters
INPUT_SIZE = 10
HIDDEN_SIZE = 64
OUTPUT_SIZE = 1
