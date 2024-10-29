FROM python:3.13.0

WORKDIR /app

COPY . /app

RUN pip install "fastapi[standard]"

# 환경 변수 설정: 기본은 production
ENV APP_ENV=production

# 개발 모드일 때만 --reload 옵션을 사용하도록 설정
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 $(if [ '$APP_ENV' = 'development' ]; then echo '--reload'; fi)"]
