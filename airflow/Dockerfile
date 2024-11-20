FROM apache/airflow:2.10.3-python3.11

USER root

RUN apt-get update && \
    apt-get install -y openjdk-17-jdk procps wget

ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PATH="$JAVA_HOME/bin:$PATH"

ENV SPARK_VERSION="3.5.3"
ENV HADOOP_VERSION="3"
RUN wget https://downloads.apache.org/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz \
    && tar -xzf spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz -C /opt \
    && mv /opt/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION /opt/spark \
    && rm spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz

ENV SPARK_HOME="/opt/spark"
ENV PATH="$SPARK_HOME/bin:$PATH"

ENV HADOOP_VERSION="3.3.6"
RUN wget https://downloads.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz \
    && tar -xzf hadoop-$HADOOP_VERSION.tar.gz -C /opt \
    && mv /opt/hadoop-$HADOOP_VERSION /opt/hadoop \
    && rm hadoop-$HADOOP_VERSION.tar.gz

ENV HADOOP_HOME="/opt/hadoop"
ENV HADOOP_CONF_DIR="$HADOOP_HOME/etc/hadoop"
ENV YARN_CONF_DIR="$HADOOP_HOME/etc/hadoop"
ENV PATH="$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

USER airflow

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
COPY ./airflow.cfg /opt/airflow/airflow.cfg

RUN pip install --no-cache-dir -r /app/requirements.txt
