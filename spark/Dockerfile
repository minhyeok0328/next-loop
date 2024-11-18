# Base image
FROM bitnami/spark:3.5.3

USER root

ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV YARN_CONF_DIR=/opt/hadoop/etc/hadoop

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update -y && apt-get install -y google-cloud-sdk

# Install Hadoop
RUN curl -O https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xzf hadoop-${HADOOP_VERSION}.tar.gz && \
    mv hadoop-${HADOOP_VERSION} ${HADOOP_HOME} && \
    rm hadoop-${HADOOP_VERSION}.tar.gz

# GCS connector setup
RUN curl -o /opt/bitnami/spark/jars/gcs-connector-hadoop3-latest.jar https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar

# Copy necessary Hadoop jar files
RUN cp ${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-client-*.jar /opt/bitnami/spark/jars/ && \
    cp ${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-common-*.jar /opt/bitnami/spark/jars/ && \
    cp ${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-api-*.jar /opt/bitnami/spark/jars/ && \
    cp ${HADOOP_HOME}/share/hadoop/common/hadoop-common-*.jar /opt/bitnami/spark/jars/ && \
    cp ${HADOOP_HOME}/share/hadoop/hdfs/hadoop-hdfs-client-*.jar /opt/bitnami/spark/jars/

# Set permissions
RUN chmod 644 /opt/bitnami/spark/jars/gcs-connector-hadoop3-latest.jar && \
    chown 1001:1001 /opt/bitnami/spark/jars/gcs-connector-hadoop3-latest.jar

# Setup Hadoop configuration directory
RUN mkdir -p /opt/hadoop/etc/hadoop && \
    chown -R 1001:1001 /opt/hadoop

USER 1001
