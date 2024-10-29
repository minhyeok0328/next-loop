#!/bin/bash

# 스크립트 실행 시 오류가 발생하면 중단
set -e

echo "Docker 및 필요한 패키지 설치 시작..."

# 시스템 패키지 업데이트
sudo apt-get update

# 필요한 패키지 설치
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Docker GPG 키 추가
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Docker 저장소 추가
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 패키지 목록 업데이트
sudo apt-get update

# Docker 설치
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

echo "Docker 설치 완료"

# Airflow 프로젝트 디렉토리 생성
mkdir -p ~/airflow/dags ~/airflow/logs ~/airflow/plugins

# 작업 디렉토리로 이동
cd ~/airflow

# Airflow UID 환경변수 설정
echo -e "\nAIRFLOW_UID=$(id -u)" > .env

echo "Airflow 디렉토리 구조 생성 완료"

# 보안 설정
sudo ufw allow 8080
sudo ufw allow 5432

echo "설치 완료! 변경사항을 적용하기 위해 시스템을 재로그인하거나 재부팅해주세요."
