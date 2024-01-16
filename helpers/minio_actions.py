from minio import Minio
from minio.error import S3Error
import os, io
from dotenv import load_dotenv


def get_minio_connection():
    minio_client = Minio(
        endpoint=os.environ.get("MINIO_ADDR"),
        access_key=os.environ.get("MINIO_ACCESS_KEY"),
        secret_key=os.environ.get("MINIO_SECRET_KEY"),
        secure=False,
    )
    try:
        minio_client.list_buckets()
        return minio_client
    except Exception as e:
        print(f"Error while connecting to minio: {e}")
        return None


def upload_to_minio(file, bucket: str):
    minio_client = get_minio_connection()
    if minio_client and minio_client.bucket_exists(bucket):
        as_bytes = file.read()
        minio_client.put_object(
            bucket_name=bucket,
            object_name=file.filename,
            data=io.BytesIO(as_bytes),
            length=len(as_bytes),
            content_type=file.content_type,
        )
        return True
    return False


def get_files(bucket: str):
    minio_client = get_minio_connection()
    objects = minio_client.list_objects(bucket_name=bucket)
    return [i.object_name for i in minio_client.list_objects(bucket_name=bucket)]


def check_if_object_exist(filename, bucket):
    minio_client = get_minio_connection()
    result = minio_client.stat_object(bucket_name=bucket, object_name=filename)
    return result


def download_from_minio(filename, bucket):
    minio_client = get_minio_connection()
    respose = minio_client.get_object(bucket_name=bucket, object_name=filename)
    return respose


def delete_from_minio(filename, bucket):
    minio_client = get_minio_connection()
    if check_if_object_exist(filename=filename, bucket=bucket):
        minio_client.remove_object(bucket_name=bucket, object_name=filename)
