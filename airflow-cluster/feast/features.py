from datetime import timedelta
from feast import Entity, Feature, FeatureView, Field, ValueType, FileSource
from feast.types import Float32, Int64
from airflow.hooks.base import BaseHook
import json
import os

# GCP 인증 설정
conn = BaseHook.get_connection('google_cloud_default')
credentials_dict = json.loads(conn.extra_dejson.get('keyfile_dict'))

# 임시 credentials 파일 생성
with open('/tmp/gcp-credentials.json', 'w') as f:
    json.dump(credentials_dict, f)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/gcp-credentials.json'

# 기존 Entity와 Feature View 정의
hotel = Entity(
    name="hotel_id",
    value_type=ValueType.INT64,
    description="hotel identifier"
)

hotel_features = FeatureView(
    name="hotel_features",
    entities=[hotel],
    ttl=timedelta(days=365),
    source=FileSource(
        path="gs://dowhat-de1-feature-store/features/hotel_features.parquet",
        timestamp_field="event_timestamp",
    ),
    schema=[
        Field(name="price", dtype=Float32),
        Field(name="rating", dtype=Float32),
        Field(name="location_score", dtype=Float32),
    ]
)
