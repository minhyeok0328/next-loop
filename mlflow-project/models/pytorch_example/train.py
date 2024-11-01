import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(project_root)

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import mlflow
import mlflow.pytorch
from datetime import datetime
import numpy as np
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests

# MLflow 설정 import
from config.mlflow_config import (
   MLFLOW_TRACKING_URI,
   MLFLOW_S3_ENDPOINT_URL,
   AWS_ACCESS_KEY_ID,
   AWS_SECRET_ACCESS_KEY,
   MLFLOW_S3_IGNORE_TLS,
   MLFLOW_HTTP_REQUEST_TIMEOUT,
   EXPERIMENT_NAME,
   MODEL_NAME,
   BATCH_SIZE,
   EPOCHS,
   LEARNING_RATE,
   INPUT_SIZE,
   HIDDEN_SIZE,
   OUTPUT_SIZE
)

def setup_mlflow_env():
    """MLflow 환경변수 설정"""
    os.environ['MLFLOW_TRACKING_URI'] = MLFLOW_TRACKING_URI
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = MLFLOW_S3_ENDPOINT_URL
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
    os.environ['MLFLOW_S3_IGNORE_TLS'] = MLFLOW_S3_IGNORE_TLS
    os.environ['MLFLOW_HTTP_REQUEST_TIMEOUT'] = MLFLOW_HTTP_REQUEST_TIMEOUT

# Session with retry strategy
session = requests.Session()
retry_strategy = Retry(
   total=3,
   backoff_factor=1,
   status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# 로깅 설정
logging.basicConfig(
   level=logging.INFO,
   format='%(asctime)s - %(levelname)s - %(message)s'
)

class SimpleDataset(Dataset):
   """간단한 예제 데이터셋"""
   def __init__(self, size=1000):
       self.x = torch.randn(size, INPUT_SIZE)
       # 예제: 입력값의 합에 약간의 노이즈를 추가
       self.y = torch.sum(self.x, dim=1).unsqueeze(1) + torch.randn(size, 1) * 0.1

   def __len__(self):
       return len(self.x)

   def __getitem__(self, idx):
       return self.x[idx], self.y[idx]

def create_data_loaders(train_size=1000, val_size=200):
   """학습 및 검증 데이터 로더 생성"""
   train_dataset = SimpleDataset(train_size)
   val_dataset = SimpleDataset(val_size)

   train_loader = DataLoader(
       train_dataset,
       batch_size=BATCH_SIZE,
       shuffle=True
   )
   val_loader = DataLoader(
       val_dataset,
       batch_size=BATCH_SIZE,
       shuffle=False
   )

   return train_loader, val_loader

def train_epoch(model, train_loader, criterion, optimizer, device):
   """한 에폭 학습"""
   model.train()
   total_loss = 0
   for batch_x, batch_y in train_loader:
       batch_x, batch_y = batch_x.to(device), batch_y.to(device)

       optimizer.zero_grad()
       output = model(batch_x)
       loss = criterion(output, batch_y)
       loss.backward()
       optimizer.step()

       total_loss += loss.item()

   return total_loss / len(train_loader)

def validate(model, val_loader, criterion, device):
   """검증 데이터로 모델 평가"""
   model.eval()
   total_loss = 0
   predictions = []
   actuals = []

   with torch.no_grad():
       for batch_x, batch_y in val_loader:
           batch_x, batch_y = batch_x.to(device), batch_y.to(device)
           output = model(batch_x)
           loss = criterion(output, batch_y)
           total_loss += loss.item()

           predictions.extend(output.cpu().numpy())
           actuals.extend(batch_y.cpu().numpy())

   val_loss = total_loss / len(val_loader)
   predictions = np.array(predictions)
   actuals = np.array(actuals)

   # Calculate additional metrics
   mse = np.mean((predictions - actuals) ** 2)
   rmse = np.sqrt(mse)
   mae = np.mean(np.abs(predictions - actuals))

   return {
       'val_loss': val_loss,
       'mse': mse,
       'rmse': rmse,
       'mae': mae
   }

def train_model():
   try:
       """전체 학습 프로세스"""
       # MLflow 설정
       mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
       mlflow.set_experiment(EXPERIMENT_NAME)

       # 디바이스 설정
       device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
       logging.info(f"Using device: {device}")

       # 데이터 로더 생성
       train_loader, val_loader = create_data_loaders()

       # 모델 초기화
       from model import SimpleModel
       model = SimpleModel(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE).to(device)

       # 손실 함수와 옵티마이저 설정
       criterion = nn.MSELoss()
       optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

       # MLflow 실험 시작
       with mlflow.start_run(run_name=f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
           # 파라미터 로깅
           mlflow.log_params({
               'input_size': INPUT_SIZE,
               'hidden_size': HIDDEN_SIZE,
               'output_size': OUTPUT_SIZE,
               'learning_rate': LEARNING_RATE,
               'batch_size': BATCH_SIZE,
               'epochs': EPOCHS,
               'optimizer': optimizer.__class__.__name__,
               'device': device.type
           })

           best_val_loss = float('inf')

           # 학습 루프
           for epoch in range(EPOCHS):
               # 학습
               train_loss = train_epoch(model, train_loader, criterion, optimizer, device)

               # 검증
               val_metrics = validate(model, val_loader, criterion, device)

               # 메트릭 로깅
               mlflow.log_metrics({
                   'train_loss': train_loss,
                   **val_metrics
               }, step=epoch)

               # 로깅
               logging.info(
                   f"Epoch {epoch+1}/{EPOCHS} - "
                   f"Train Loss: {train_loss:.4f} - "
                   f"Val Loss: {val_metrics['val_loss']:.4f} - "
                   f"RMSE: {val_metrics['rmse']:.4f}"
               )

               # 모델 저장 (검증 손실이 개선된 경우)
               if val_metrics['val_loss'] < best_val_loss:
                   best_val_loss = val_metrics['val_loss']
                   
                   # 입력 예제와 signature 생성
                   input_example = torch.randn(1, INPUT_SIZE)
                   signature = mlflow.models.infer_signature(
                       model_input=input_example.numpy(),
                       model_output=model(input_example.to(device)).cpu().detach().numpy()
                   )
                   
                   # 모델 저장
                   mlflow.pytorch.log_model(
                       model, 
                       "best_model",
                       signature=signature,
                       input_example=input_example.numpy()
                   )
                   logging.info(f"Saved new best model with val_loss: {best_val_loss:.4f}")

           # 최종 모델 저장
           input_example = torch.randn(1, INPUT_SIZE)
           signature = mlflow.models.infer_signature(
               model_input=input_example.numpy(),
               model_output=model(input_example.to(device)).cpu().detach().numpy()
           )
           
           model_info = mlflow.pytorch.log_model(
               model, 
               "final_model",
               signature=signature,
               input_example=input_example.numpy()
           )

           logging.info(f"Training completed. Model saved: {model_info.model_uri}")
           return model_info

   except Exception as e:
       logging.error(f"Error during training: {str(e)}")
       raise

def test_mlflow_connection():
   try:
       logging.info("Testing MLflow connection...")
       client = mlflow.tracking.MlflowClient()
       experiments = client.search_experiments()
       logging.info("MLflow connection successful!")
       return experiments
   except Exception as e:
       logging.info(f"MLflow connection failed: {str(e)}")
       raise

if __name__ == "__main__":
   try:
       # MLflow 환경 설정
       setup_mlflow_env()

       # 연결 테스트
       test_mlflow_connection()
       
       logging.info("Starting training...")
       model_info = train_model()
       logging.info("Training completed successfully!")
   except Exception as e:
       logging.error(f"Error during training: {str(e)}")
       raise
