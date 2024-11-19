FROM apache/airflow:2.10.3-python3.11
USER root

# System dependencies
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Python symbolic links
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.11 /usr/bin/python

# Set JAVA_HOME for OpenJDK 17
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

USER airflow
# Install Python packages
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Reset entrypoint
ENTRYPOINT ["/usr/bin/dumb-init", "--", "/entrypoint"]
