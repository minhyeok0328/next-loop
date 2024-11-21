import os
import mlflow
import traceback
import pandas as pd

from dotenv import load_dotenv
from mlflow.tracking import MlflowClient
from fastapi import FastAPI, HTTPException
from models import PredictionInput, PredictionOutput
from prometheus_fastapi_instrumentator import Instrumentator


load_dotenv()

def setup_mlflow(experiment_name):
    mlflow.set_tracking_uri("http://10.178.0.10:5000")
    mlflow.set_experiment(experiment_name)

app = FastAPI(
    title="Titanic Survival Prediction API",
    description="Predict survival probability for Titanic passengers",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)

# 전역 변수
model = None
model_name = "titanic-randomforest"
model_version = None
client = None

@app.on_event("startup")
async def startup_event():
    global model, client, model_version
    try:
        # MLflow 설정
        setup_mlflow("titanic-classification")
        client = MlflowClient()
        
        # 먼저 production 모델 찾기
        for mv in client.search_model_versions(f"name='{model_name}'"):
            if mv.current_stage == "Production":
                model_version = mv.version
                break
        
        # production 모델이 없으면 최신 버전 사용
        if model_version is None:
            versions = client.search_model_versions(f"name='{model_name}'")
            if not versions:
                raise Exception(f"❌No versions found for model {model_name}")
            model_version = max([mv.version for mv in versions])
            print(f"❌No production model found, using latest version {model_version}")
        
        # 모델 로드
        if model_version:
            model = mlflow.pyfunc.load_model(
                model_uri=f"models:/{model_name}/{model_version}"
            )
            print(f"✅ Loaded {model_name} version {model_version}")
        else:
            raise Exception("❌No model versions found")
        
    except Exception as e:
        print(f"❌Error loading model: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # 입력 데이터를 DataFrame으로 변환
        input_df = pd.DataFrame([[
            input_data.pclass,
            input_data.age,
            input_data.fare,
            input_data.sex
        ]], columns=['Pclass', 'Age', 'Fare', 'Sex'])
        
        # 예측
        prediction = model.predict(input_df)[0]
        
        # 확률값 계산 (모델이 predict_proba를 지원하는 경우)
        try:
            probability = model.predict_proba(input_df)[0][1]
        except:
            probability = float(prediction)
        
        return PredictionOutput(
            survival_probability=probability,
            prediction=int(prediction),
            version=f"{model_name}@{model_version}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/info")
async def model_info():
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # 모델의 메타데이터 가져오기
    model_metadata = client.get_model_version(model_name, model_version)
    
    return {
        "model_name": model_name,
        "model_version": model_version,
        "creation_timestamp": model_metadata.creation_timestamp,
        "last_updated_timestamp": model_metadata.last_updated_timestamp,
        "features": ["Pclass", "Age", "Fare", "Sex"],
        "description": model_metadata.description if model_metadata.description else "No description available"
    }