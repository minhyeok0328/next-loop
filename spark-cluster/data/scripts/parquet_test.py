from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, DoubleType
import random
from datetime import datetime, timedelta

def create_test_dataset(spark, num_records=1000000):
    """대용량 테스트 데이터 생성"""
    
    # 스키마 정의
    schema = StructType([
        StructField("user_id", StringType(), False),
        StructField("timestamp", TimestampType(), False),
        StructField("category", StringType(), False),
        StructField("amount", DoubleType(), False),
        StructField("item_count", IntegerType(), False),
        StructField("region", StringType(), False)
    ])

    # 샘플 데이터 생성
    base_date = datetime.now()
    categories = ["Electronics", "Clothing", "Food", "Books", "Sports"]
    regions = ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon"]
    
    data = []
    for i in range(num_records):
        data.append((
            f"user_{i % 10000:05d}",
            base_date + timedelta(minutes=i % 1440),
            random.choice(categories),
            round(random.uniform(10.0, 1000.0), 2),
            random.randint(1, 10),
            random.choice(regions)
        ))
    
    # DataFrame 생성
    df = spark.createDataFrame(data, schema)
    return df

def write_parquet_with_partitions(df, path, partition_cols):
    """파티셔닝된 Parquet 파일 쓰기"""
    df.write.partitionBy(partition_cols)\
        .mode("overwrite")\
        .parquet(path)

def main():
    # Spark 세션 생성
    spark = SparkSession.builder\
        .appName("Parquet Test")\
        .getOrCreate()

    try:
        # 데이터셋 생성
        print("데이터셋 생성 중...")
        df = create_test_dataset(spark)
        
        # 기본 통계 출력
        print("\n기본 데이터셋 정보:")
        df.printSchema()
        print(f"전체 레코드 수: {df.count()}")
        
        # 파티셔닝 없이 저장
        print("\n파티셔닝 없이 Parquet 저장 중...")
        df.write.mode("overwrite").parquet("/opt/spark/data/sales_no_partition.parquet")
        
        # 파티셔닝하여 저장
        print("\n파티셔닝하여 Parquet 저장 중...")
        write_parquet_with_partitions(df, 
                                    "/opt/spark/data/sales_partitioned.parquet",
                                    ["region", "category"])
        
        # 저장된 데이터 읽기 테스트
        print("\n저장된 Parquet 파일 읽기 테스트:")
        
        # 전체 데이터 읽기
        df_read = spark.read.parquet("/opt/spark/data/sales_partitioned.parquet")
        print("\n특정 지역의 판매 통계:")
        df_read.groupBy("region")\
            .agg({"amount": "sum", "item_count": "sum"})\
            .show()
        
        # 특정 파티션만 읽기
        print("\n서울 지역 전자제품 판매 데이터:")
        df_filtered = spark.read.parquet("/opt/spark/data/sales_partitioned.parquet")\
            .where("region = 'Seoul' AND category = 'Electronics'")
        df_filtered.show(5)

    finally:
        spark.stop()

if __name__ == "__main__":
    main()
