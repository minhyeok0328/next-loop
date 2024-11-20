from datetime import timedelta
from feast import Entity, FeatureView, FileSource
from feast.types import Int64, String, Float32, Timestamp
from feast.field import Field


csv_file_source = FileSource(
    path = "gs://dowhat-de1-datawarehouse/api/v1/hotel_order/**/*.parquet",
    event_timestamp_column="reg_date",
    created_timestamp_column="check_date",
)

order_entity = Entity(
    name="order_seq",
    join_key="order_seq",
    description="Unique identifier for each order",
)

# Feature View 정의
order_feature_view = FeatureView(
    name="order_features",
    entities=[order_entity],
    ttl=timedelta(days=1),
    schema=[
        Field(name="room_seq", dtype=Int64),
        Field(name="customer_seq", dtype=Int64),
        Field(name="order_price", dtype=Float32),
        Field(name="status", dtype=String),
        Field(name="room_building_seq", dtype=Int64),
        Field(name="room_floor_seq", dtype=Int64),
        Field(name="visitor_cnt", dtype=Int64),
        Field(name="visit_adult_cnt", dtype=Int64),
        Field(name="visit_child_cnt", dtype=Int64),
        Field(name="visit_baby_cnt", dtype=Int64),
        Field(name="check_in", dtype=Timestamp),
        Field(name="check_out", dtype=Timestamp),
        Field(name="check_out_expected", dtype=Timestamp),
        Field(name="item_seq", dtype=Int64),
        Field(name="item_name", dtype=String),
        Field(name="item_count", dtype=Int64),
        Field(name="department_seq", dtype=Int64),
        Field(name="price", dtype=Float32),
        Field(name="waiting_period", dtype=Int64),
        Field(name="delay_period", dtype=Int64),
        Field(name="free_count", dtype=Float32),
        Field(name="coupon_seq", dtype=Int64),
        Field(name="result_price", dtype=Float32),
        Field(name="complete_period", dtype=Float32),
    ],
    source=csv_file_source,
)

if __name__ == "__main__":
    from feast import FeatureStore

    store = FeatureStore(repo_path=".")
    store.apply([order_feature_view, order_entity])
