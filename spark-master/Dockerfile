FROM bitnami/spark:3.5.3
USER root

# Install Python 3.11
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3.11-distutils \
        python3-pip \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python symbolic links
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.11 /usr/bin/python

# Install PySpark
RUN pip3 install --no-cache-dir pyspark==3.5.3

# Set Python environment variables
ENV PYSPARK_PYTHON=/usr/bin/python3.11
ENV PYTHONPATH=/usr/local/lib/python3.11/dist-packages:/usr/lib/python3.11/dist-packages
ENV SPARK_HOME=/opt/bitnami/spark

USER 1001
