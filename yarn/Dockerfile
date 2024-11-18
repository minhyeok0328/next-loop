FROM openjdk:8-jdk

# Hadoop 버전 설정
ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV YARN_CONF_DIR=/opt/hadoop/etc/hadoop

# 기본 도구 설치
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Hadoop 설치
RUN curl -O https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xzf hadoop-${HADOOP_VERSION}.tar.gz && \
    mv hadoop-${HADOOP_VERSION} ${HADOOP_HOME} && \
    rm hadoop-${HADOOP_VERSION}.tar.gz

# 설정 디렉토리 생성
RUN mkdir -p $HADOOP_CONF_DIR

# 권한 설정
RUN groupadd hadoop && \
    useradd -ms /bin/bash -g hadoop yarn && \
    chown -R yarn:hadoop $HADOOP_HOME

USER yarn

CMD ["sh", "-c", "if [ \"$YARN_NODEMANAGER_HOSTNAME\" != \"\" ]; then $HADOOP_HOME/bin/yarn nodemanager; else $HADOOP_HOME/bin/yarn resourcemanager; fi"]
