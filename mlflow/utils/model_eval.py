# utils/model_eval.py
import mlflow
import mlflow.sklearn
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from utils.mlflow import promote_best_model

def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    return {
        'accuracy': accuracy_score(y_test, predictions),
        'precision': precision_score(y_test, predictions),
        'recall': recall_score(y_test, predictions),
        'f1': f1_score(y_test, predictions)
    }

def create_run_name(model_name, params):
    """모델명과 주요 파라미터를 포함한 run name 생성"""
    param_str = '_'.join(f"{k}={v}" for k, v in params.items())
    return f"{model_name}_{param_str}"

def train_and_evaluate_models(models, X_train, X_test, y_train, y_test, eval_metric='f1'):
    best_model_info = {eval_metric: 0}
    
    for model_name, model_config in models.items():
        for params in model_config['params']:
            # run name 생성
            run_name = create_run_name(model_name, params)
            
            with mlflow.start_run(run_name=run_name):
                model = model_config['model']
                model.set_params(**params)
                model.fit(X_train, y_train)
                
                metrics = evaluate_model(model, X_test, y_test)
                mlflow.log_params(params)
                mlflow.log_metrics(metrics)
                mlflow.sklearn.log_model(
                    model, 
                    "model",
                    registered_model_name=f"titanic-{model_name}"
                )

                if metrics[eval_metric] > best_model_info[eval_metric]:
                    best_model_info = {
                        eval_metric: metrics[eval_metric],
                        'run_id': mlflow.active_run().info.run_id,
                        'model_name': f"titanic-{model_name}"
                    }
    
    promote_best_model(best_model_info)