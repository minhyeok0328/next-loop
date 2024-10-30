FROM python:3.13.0

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 환경 변수 설정: 기본은 production
ENV APP_ENV=production

COPY . /app

# 개발 모드일 때만 --reload 옵션을 사용하도록 설정
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
