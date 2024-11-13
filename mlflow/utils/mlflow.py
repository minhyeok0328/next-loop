# utils/mlflow.py
import mlflow
from mlflow.tracking import MlflowClient
import time

def setup_mlflow(experiment_name):
    mlflow.set_tracking_uri("http://10.178.0.10:5000")
    mlflow.set_experiment(experiment_name)

def set_model_alias(client, name, version, alias):
    """모델 버전에 별칭을 설정하는 함수"""
    try:
        # version을 문자열로 변환
        version = str(version)
        client.set_registered_model_alias(name, alias, version)
    except Exception as e:
        print(f"❌Warning: Could not set alias {alias} for model {name}: {e}")

def promote_best_model(best_model_info):
    client = MlflowClient()
    
    # 기존 Production 모델을 찾아서 archived로 별칭 변경
    for mv in client.search_model_versions(f"name='{best_model_info['model_name']}'"):
        if mv.current_stage == "Production":
            try:
                set_model_alias(client, mv.name, mv.version, "archived")
            except Exception as e:
                print(f"❌Warning: Could not archive model version {mv.version}: {e}")

    # best run의 model version 찾기
    run = mlflow.get_run(best_model_info['run_id'])
    best_version = None
    
    for mv in client.search_model_versions(f"name='{best_model_info['model_name']}'"):
        if mv.run_id == best_model_info['run_id']:
            best_version = mv.version
            break
            
    if best_version is None:
        print("❌Error: Could not find the best model version")
        return
    
    # 최고 성능 모델을 production으로 별칭 설정
    try:
        set_model_alias(client, best_model_info['model_name'], best_version, "production")
        
        # 모델 메타데이터 설정
        timestamp = str(int(time.time()))
        metric_value = str(best_model_info[list(best_model_info.keys())[0]])
        
        client.set_registered_model_tag(best_model_info['model_name'], "last_updated", timestamp)
        client.set_registered_model_tag(best_model_info['model_name'], "best_metric", metric_value)
        
        print(f"✅ Successfully promoted {best_model_info['model_name']} (version {best_version}) to production with {metric_value}")
    except Exception as e:
        print(f"❌Warning: Could not promote model version {best_version}: {e}")

def load_production_model(model_name):
    """
    Production 별칭이 설정된 모델을 로드하는 함수
    """
    try:
        model = mlflow.pyfunc.load_model(
            model_uri=f"models:/{model_name}@production"
        )
        return model
    except Exception as e:
        print(f"❌Error loading production model: {e}")
        # 대체로 최신 버전 로드
        model = mlflow.pyfunc.load_model(
            model_uri=f"models:/{model_name}/latest"
        )
        return model