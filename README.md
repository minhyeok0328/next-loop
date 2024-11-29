# Dowhat 기업 연계 프로젝트 

--- 
## 🏨 프로젝트 정보 

- **프로젝트 명**: 호텔 운영 효율화 및 AI CRM 파이프라인 구축
- **소속 기관**: 2024 이어드림스쿨 4기  
- **개발 기간**: 2024.10.15. ~ 2024.11.22.
---
  
## 👫 NextLoop팀 소개 

![image](https://github.com/user-attachments/assets/734f6e3c-0487-4727-9635-38d13c266c37)

- **끊임없는 발전**  
   - 'Next'는 항상 다음 단계로 나아가는 것을 뜻함, 이는 계속해서 더 나은 솔루션과 기술을 탐구하고 도전한다는 의미를 담고 있음
     
- **순환적 개선**  
   - 'Loop'는 프로그래밍에서 반복을 뜻함, 이는 코드나 제품을 지속적으로 개선하고 최적화하는 개발 과정을 상징함.
     
- **미래 지향성**  
   - 변화와 발전을 멈추지 않고, 항상 다음 단계를 생각하고 준비하는 미래 지향적인 팀이라는 이미지를 전달.

---

## ✅ NextLoop Repository 방문 횟수 

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fminhyeok0328%2Fnext-loop&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)



---
## 🛠 Stacks

- **Environment**: ![VS Code](https://img.shields.io/badge/Visual%20Studio%20Code-blue?logo=visual-studio-code&logoColor=white) ![Git](https://img.shields.io/badge/Git-orange?logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/GitHub-black?logo=github&logoColor=white)
- **Development**: ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) ![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?logo=apache-airflow&logoColor=white) ![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?logo=apache-spark&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![MLflow](https://img.shields.io/badge/MLflow-0194E2?logo=mlflow&logoColor=white) ![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white) ![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white) ![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)



- **Communication**: ![Slack](https://img.shields.io/badge/Slack-4A154B?logo=slack&logoColor=white) ![Notion](https://img.shields.io/badge/Notion-000000?logo=notion&logoColor=white)
 

---

## 🔅 주요 기능 

- **데이터 파이프라인 구축**
   - 제공받은 Dowhat 데이터를 GCS에 적재.
   - 주 단위로 Airflow 배치 태스크를 통해 데이터를 인입하는 데이터 파이프라인 구현.
   - 현재는 로컬에서 Spark를 사용, 추후 데이터 규모가 많아질 경우를 대비해서 Spark cluster 구축해 둠.

- **MLOps 파이프라인 구축**
   - 제공받은 Dowhat 데이터를 전처리하여 간단한 추천 모델 학습.
   - mlflow를 통해 모델 실험 관리(Tracking), 모델 레지스트리 기능 사용.
   - FastAPI를 통해 모델 서빙 구현.
   - Github action, Nginx를 활용한 Blue-Green 무중단 배포 방식을 통해 CI/CD 구현.
 
- **모니터링 시스템 구축**
   - Prometheus, Grafana를 통해 시스템 성능 모니터링 및 slack 알람 연동.
   - cAdvisor, prometheus Fastapi instrumentator를 통해 메트릭 정보 수집.
     

---
## 🖥️ 개발 환경 설정

- **GCP 인스턴스 사용**
  - 리전: 서울 (asia-northeast3) 
  - Image : Ubuntu 24.04.1 LTS(x86/64) 단, MLFlow 등 모델 학습 인스턴스는 Deep Learning VM with CUDA 12.3 M125
  - Instance Type :  E2.standard-4 (vcpu 4, ram 16gb)
  - Storage : 최소 100GB (균형 있는 영구 디스크)

- **기타 주의사항**
  - 각 인스턴스 하나에 하나의 서비스 만을 띄워야 함. 
    다만 **Prometheus, Grafana**같이 부하가 별로 없는 서비스의 경우 같은 인스턴스에 배포하여도 상관없음.
  - 인스턴스 이름은 **dowhat-{platform}-{number}** 
    ex) dowhat-monitoring-1   



---


## 🖊 아키텍처

### **1. 전체 아키텍처** 
![image](https://github.com/user-attachments/assets/3dbbe9fb-90c4-4033-ab9b-769772fb8c1a)

- Airflow의 역할
  - GCS에서 CSV 파일 검색 및 관리: GCSHook을 사용해 Google Cloud Storage 버킷에서 CSV 파일 리스트를 추출.
  - Spark 작업 실행, GCS에 결과 저장.
  - 임시 키 파일 생성 및 보안 관리: Airflow는 Google Cloud 서비스 계정 키를 임시 파일로 생성하여 보안성을 강화.
  - Spark 작업 트리거: Spark 작업은 CSV 파일을 읽고 데이터를 전처리하여 Parquet 형식으로 변환.<br>


  
![image](https://github.com/user-attachments/assets/cae3ce0d-dcad-4582-a13d-e453f04da21b) <br>


### **2.파이프라인 상세 구조**
![image](https://github.com/user-attachments/assets/8da81757-4720-4548-bd5f-f1b66901de49)


- 데이터 파이프라인은 4개의 주요 단계로 구성되어 있음.<br>

#### 1) Storage Layer (입력 저장 단계)
- 데이터 소스:
  - CSV 파일 업로드를 통해 데이터를 입력받음.
  - GCS(Google Cloud Storage)에 데이터를 저장.



#### 2) Processing Layer (데이터 처리 단계)
- Apache Spark를 사용하여 3단계 데이터 처리 수행.
  - 데이터 검증 (Data Validation): 데이터를 검증하고 품질을 확인.
  - 변환 (Transformation): 호텔 도메인에 기반한 feature 생성 및 데이터 전처리.
  - 포맷 변환 (Format Convert): 데이터를 효율적으로 저장 및 활용할 수 있도록 'Parquet' 포맷으로 변환.


#### 3) Storage Layer (출력 저장 단계)
  - 최종 처리된 데이터를 feature store인 Cloud Storage Bucket에 저장.
  - feast를 사용하지 않은 이유는 인프라 구축 초기 단계이기 때문에 최대한 간소화하기로 결정했기 때문임. 


#### 4) Consumption Layer (소비 단계)
  - 최종 데이터는 데이터 사이언티스트들이 Feature Store에서 데이터를 가져와 분석 및 모델 학습 등에 활용.


### **3.Mlops파이프라인 상세 구조**
![image](https://github.com/user-attachments/assets/15ea07f8-c0c0-4b92-95b2-355b674bc189)

#### 1) 데이터 수집 및 로드
- 원천 데이터는 Google Cloud Storage를 통해 수집 및 관리됨. 


#### 2) 모델 학습 및 실험 관리
- 수집된 데이터를 활용해 학습 데이터셋으로 변환.

#### 3) Mlflow
- Dockerfile을 만들어서 MLflow 서버를 컨테이너 환경에서 실행.
- Google Cloud Storage와 PostgreSQL과 같은 외부 리소스를 활용한 실험 및 모델 관리가 가능하도록 설정.
- mlflow의 기능으로 2가지가 있음. 
  - Tracking
    - 실험 기록 및 비교: 모델 학습 시 학습 파라미터(학습률, 배치 크기 등), 평가 메트릭(정확도, 손실 등), 모델 아티팩트(학습된 모델 파일)를 관리. 
    - 실험 재현성 보장: MLflow Tracking을 통해 과거 실험의 상세 정보(코드, 데이터, 환경)를 손쉽게 복원하여 동일한 결과를 재현할 수 있음.

  - Model Registry
    - 모델 버전 관리: 
      - 학습된 모델은 Model Registry에 저장되며, 각 모델은 고유한 버전으로 관리.  
      - 이를 통해 이전 모델로 롤백하거나 다양한 모델을 비교할 수 있음.
  
    - 모델 상태 관리: 모델의 상태를 3단계로 나눠, 배포 단계 및 사용 여부를 명확히 함. 
      - Staging: 실험 조건에 맞는 상위 n개 모델.
      - Production: 실제 서비스 중인 모델, 배포 대상으로 지정됨. 
      - Archived: Porduction에 있던 과거 모델은 archived로 변경. 

   

#### 4) CI/CD: GitHub Actions와 NGINX를 활용한 배포
- Github action
  - 새로운 모델 배포 이후 Backend 서버(FastAPI)에서 변경된 내역 확인.(backend/** 디렉터리에서 변경이 발생하면 detect-changes 작업에서 확인 가능)
  - 업데이트 된 코드를 바탕으로
    - Blue-Green 배포 스크립트(switch-blue-green.sh)를 실행.
    - 변경 사항을 Green 컨테이너에 반영. 
    
- Blue-Green Deployment
  - nginx의 reverse proxy를 통해 새 버전으로 트래픽을 전환하는 방식이라 무중단 배포가 가능
  - 새로운 모델 배포 시 문제가 생기면 트래픽을 구버전으로 신속히 롤백할 수 있어 높은 안정성 확보 가능.  
    - Blue App: 기존 모델 서비스.
    - Green App: 새로 배포된 모델 서비스.

![image](https://github.com/user-attachments/assets/86d9a467-ea5b-4591-b4a7-37e74e3ec93a)


---
## 🔔 모니터링
![image](https://github.com/user-attachments/assets/99c324b5-a783-4f89-9fd8-6b642801bc8e)

### 프로메테우스
- 데이터 수집 방식: pull 방식 선택, 모니터링 대상 각각의 서버마다 설치하지 않고 monitoring 서버에만 prometheus를 설치함. 
- Logstash나 Telegraf같은 Pushing 방식보다 모니터링 서버에 영향을 덜 주기 때문에 모니터링 도구로 선택하게 되었음. 

### 그라파나
- 차트와 그래프를 활용해 데이터를 시각화 할 수 있어 모니터링 도구로 선택하게 되었음. 

### 모니터링 네트워크 설정
- node exporter의 경우 서버를 모니터링 하는 것이기 때문에 다양한 메트릭을 수집할 수 없어서 아래와 같은 도구 사용 
  - Prometheus FastAPI Instrumentator: FastAPI 애플리케이션에서 메트릭을 자동으로 수집하기 위한 Python 라이브러리, 'http'이름으로 시작되는 메트릭들을 확인할 수 있음.
  - cAdvisor: Docker 컨테이너의 CPU, 메모리, 네트워크 사용량 등 다양한 메트릭을 수집, 'container'이름으로 시작되는 메트릭들을 확인할 수 있음.
- Airflow, Mlflow, Fastapi, Monitoring 서버 모두 같은 네트워크로 연결.

![image](https://github.com/user-attachments/assets/add0bc53-bc5e-4800-893c-af0355a0dc53)
  
  
![image](https://github.com/user-attachments/assets/5a1acb14-15fc-476f-a595-244ad635defd)

![image](https://github.com/user-attachments/assets/41e20b78-6652-4cdf-886f-802741ce3e42)


