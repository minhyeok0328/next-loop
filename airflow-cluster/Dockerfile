FROM apache/airflow:2.7.1

USER root

# Java 설치
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk procps && \
    apt-get clean

# JAVA_HOME 설정
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --user -r /requirements.txt
