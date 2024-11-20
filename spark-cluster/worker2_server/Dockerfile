# 베이스 이미지로 bitnami/spark:3.5.1 사용
FROM bitnami/spark:3.5.3

# root 사용자 권한으로 전환
USER root

# 필요한 패키지 설치 (curl, wget, ping, net-tools, vim 등) 및 boto3 설치
RUN apt-get update && \
    apt-get install -y curl wget iputils-ping net-tools vim && \
    pip install boto3 Pillow

# spark-prometheus-native metric 모니터링 관련 설정 파일
COPY metrics.properties /opt/bitnami/spark/conf/metrics.properties

# 작업 디렉토리를 /opt/bitnami/spark으로 설정
WORKDIR /opt/bitnami/spark