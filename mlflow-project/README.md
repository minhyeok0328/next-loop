# MLflow Project

## 설정 방법
1. 환경 변수 설정
   - config/.env 파일을 수정하여 필요한 환경 변수 설정

2. Docker 컨테이너 실행
   ```bash
   docker-compose up -d
   ```

3. MLflow UI 접속
   - http://localhost:5000

## 프로젝트 구조
- docker/: Docker 관련 파일
- models/: ML 모델 코드
- notebooks/: Jupyter notebooks
- config/: 설정 파일
- scripts/: 유틸리티 스크립트
- tests/: 테스트 코드
