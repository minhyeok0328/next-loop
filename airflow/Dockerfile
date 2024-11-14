FROM apache/airflow:2.7.1-python3.11

USER root

RUN apt-get update && \
    apt-get install -y openjdk-11-jdk procps wget

ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk-arm64"
ENV PATH="$JAVA_HOME/bin:$PATH"

ENV SPARK_VERSION="3.5.3"
ENV HADOOP_VERSION="3"
RUN wget https://downloads.apache.org/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz \
    && tar -xzf spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz -C /opt \
    && mv /opt/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION /opt/spark \
    && rm spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz

ENV SPARK_HOME="/opt/spark"
ENV PATH="$SPARK_HOME/bin:$PATH"

USER airflow

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt
