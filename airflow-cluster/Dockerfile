FROM apache/airflow:2.7.1-python3.11

USER root
# Install OpenJDK
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk procps && \
    apt-get clean
# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
# Install required packages
RUN apt-get update && apt-get install -y wget
# Install Spark
ENV SPARK_VERSION=3.4.2
ENV HADOOP_VERSION=3
RUN wget https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xvzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz
# Set Spark environment variables
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin
# Install GCS connector
RUN wget https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar -P $SPARK_HOME/jars/
# Create necessary directories
RUN mkdir -p /opt/airflow/jars && \
    cp $SPARK_HOME/jars/gcs-connector-hadoop3-latest.jar /opt/airflow/jars/
# Copy requirements file
COPY requirements.txt /requirements.txt
USER airflow
# Install PySpark and other requirements
RUN pip install --no-cache-dir pyspark==${SPARK_VERSION} && \
    pip install --no-cache-dir apache-airflow-providers-apache-spark && \
    pip install --no-cache-dir -r /requirements.txt
