# main.py
import argparse
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from utils.data import load_and_preprocess_data
from utils.model_eval import train_and_evaluate_models
from utils.mlflow import setup_mlflow, load_production_model

def get_models():
    return {
        'randomforest': {
            'model': RandomForestClassifier(random_state=42),
            'params': [
                {'n_estimators': 100, 'max_depth': 10},
                {'n_estimators': 200, 'max_depth': 15}
            ]
        },
        'gradient_boosting': {
            'model': GradientBoostingClassifier(random_state=42),
            'params': [
                {'n_estimators': 100, 'learning_rate': 0.1},
                {'n_estimators': 200, 'learning_rate': 0.05}
            ]
        },
        'svm': {
            'model': SVC(),
            'params': [
                {'C': 1.0, 'kernel': 'rbf'},
                {'C': 2.0, 'kernel': 'linear'}
            ]
        }
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', type=str, default='titanic-classification',
                      help='Name of the MLflow experiment')
    parser.add_argument('-e', '--eval_metric', type=str, default='f1',
                      choices=['f1', 'accuracy', 'precision', 'recall'],
                      help='Evaluation metric for model selection')
    parser.add_argument('--data_url', type=str, 
                      default="gs://dowhat-de1-mlfllowtest/titanic/titanic.csv",
                      help='URL of the dataset')
    args = parser.parse_args()

    # MLflow 설정
    setup_mlflow(args.name)

    # 데이터 로드 및 전처리
    X_train, X_test, y_train, y_test = load_and_preprocess_data(args.data_url)

    # 모델 학습 및 평가
    models = get_models()
    train_and_evaluate_models(models, X_train, X_test, y_train, y_test, args.eval_metric)

if __name__ == "__main__":
    main()