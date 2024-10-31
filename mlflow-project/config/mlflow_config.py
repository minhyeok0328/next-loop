### config/mlflow_config.py ###
### gcp instance update ###
### minIO 자격증명문제 update ###

import os
from dotenv import load_dotenv
load_dotenv()

EXTERNAL_IP = "34.64.68.155"  #외부IP변경 GCP Instance

# MLflow 설정
MLFLOW_TRACKING_URI = f"http://localhost:5000"
MLFLOW_S3_ENDPOINT_URL = f"http://localhost:9000"
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
