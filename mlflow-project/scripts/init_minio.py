from minio import Minio

def init_minio():
    # MinIO 클라이언트 생성
    client = Minio(
        "localhost:9000",
        access_key="minio",
        secret_key="minio123",
        secure=False
    )

    # mlflow 버킷이 없으면 생성
    if not client.bucket_exists("mlflow"):
        client.make_bucket("mlflow")
        print("Successfully created 'mlflow' bucket")
    else:
        print("'mlflow' bucket already exists")

if __name__ == "__main__":
    init_minio()
