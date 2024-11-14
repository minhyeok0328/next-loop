# MLFLOW SETUP
### backend store uri
- Cloud SQL(postgres)
    ```bash
    # psql 설치 (없다면)
    sudo apt-get install postgresql-client

    # 직접 연결 테스트
    psql "host=${CloudSQP_public_ip} port=5432 dbname=${dbname} user=${user} password=${password}"

### mlflow
- mlflow server up
    ```bash
    # Docker 이미지 빌드
    sudo docker build -t mlflow-server .

    # Docker 컨테이너 실행
    sudo docker run -d -p 5000:5000 --name mlflow-server mlflow-server
    ```
- main.py ```get_models```함수에서 사용 model 및 params 설정
    ```bash
    # 모델 실험 tarin
    python main.py -n ${experiment_name} -e ${evaluation_metric} -data_url ${data_url}
    ```
- web ui에서 실험 결과 확인: ```mlflow-server-instance_public_ip:mlflow_port```
-  ```artifact-root```에서 모델 실험 결과 ```mlflow-artifacts``` 확인
