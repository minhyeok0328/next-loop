from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import argparse

def process_csv_to_parquet(input_bucket, output_bucket, input_files):
    spark = SparkSession.builder.appName("CSVToParquet").getOrCreate()

    for file in input_files:
        # CSV 파일 읽기
        df = spark.read.csv(f"gs://{input_bucket}/{file}", header=True, inferSchema=True)
        
        # Null 값 제거 및 필요한 전처리 수행
        cleaned_df = df.dropna()  # Null 값 제거

        # Parquet로 저장
        output_path = file.replace("csv_files", "parquet_files").replace(".csv", ".parquet")
        cleaned_df.write.parquet(f"gs://{output_bucket}/{output_path}", mode='overwrite')

    spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_bucket", required=True, help="GCS bucket containing the input CSV files")
    parser.add_argument("--output_bucket", required=True, help="GCS bucket for the output Parquet files")
    parser.add_argument("--input_files", nargs='+', required=True, help="List of CSV files to process")
    
    args = parser.parse_args()
    process_csv_to_parquet(args.input_bucket, args.output_bucket, args.input_files)
