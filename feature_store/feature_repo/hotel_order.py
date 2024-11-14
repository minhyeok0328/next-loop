from datetime import timedelta
from feast import Entity, Feature, FeatureView, FileSource
from feast.types import Int64, String, Float32
from feast.value_type import ValueType
from feast.field import Field

# 데이터 소스 정의
csv_file_source = FileSource(
    path="data/data.parquet", 
    event_timestamp_column="reg_date",
    created_timestamp_column="check_date",
)

# 엔티티 정의
order_entity = Entity(
    name="order_seq",
    value_type=ValueType.INT64,
    description="Unique identifier for each order"
)

# Feature View 정의
order_feature_view = FeatureView(
    name="order_features",
    entities=[order_entity],
    ttl=timedelta(days=1),
    schema=[
        Field(name="room_seq", dtype=String),
        Field(name="customer_seq", dtype=Int64),
        Field(name="order_price", dtype=Float32),
        Field(name="status", dtype=String),
        Field(name="room_building_seq", dtype=Int64),
        Field(name="room_floor_seq", dtype=Int64),
        Field(name="visitor_cnt", dtype=Int64),
        Field(name="visit_adult_cnt", dtype=Int64),
        Field(name="visit_child_cnt", dtype=Int64),
        Field(name="visit_baby_cnt", dtype=Int64),
    ],
    source=csv_file_source,
)

# Feature View 등록
if __name__ == "__main__":
    from feast import FeatureStore

    store = FeatureStore(repo_path=".")
    store.apply([order_feature_view, order_entity])

