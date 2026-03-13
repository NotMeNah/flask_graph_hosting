from minio import Minio
from minio.error import S3Error
from datetime import timedelta
from .base import ImageStorage
from werkzeug.datastructures import FileStorage
import config

class MinioStorage(ImageStorage):
    def __init__(self):
        self.client=Minio(
            endpoint=config.MINIO_ENDPOINT,
            access_key=config.MINIO_ACCESS_KEY,
            secret_key=config.MINIO_SECRET_KEY,
            secure=config.MINIO_SECURE
        )
        self.bucket_name=config.MINIO_BUCKET_NAME
        self._create_bucket_if_not_exists()


    def _create_bucket_if_not_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise RuntimeError(f"创建 Minio 桶失败：{str(e)}")

    def save_image(self,file:FileStorage,filename:str)->str:
        try:
            file.stream.seek(0,2)
            file_size=file.stream.tell()
            file.stream.seek(0)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=filename,
                data=file.stream,
                length=file_size,
                content_type=file.content_type
            )
            return filename
        except S3Error as e:
            raise RuntimeError(f"上传图片到 Minio 失败：{str(e)}")

    def get_file_identifier(self,graph_id:str)->str | None:
        for ext in[".jpg",".jpeg",".png",".gif",".webp"]:
            obj_name=f"{graph_id}{ext}"
            try:
                self.client.stat_object(self.bucket_name,obj_name)
            except S3Error:
                continue
            return obj_name
        return None

    def get_image_url(self,file_identifier:str)->str:
        if not file_identifier:
            raise RuntimeError("生成URL失败：文件识别不能为空")
        try:
            url=self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=file_identifier,
                expires=timedelta(days=7)
            )
        except S3Error as e:
            raise RuntimeError(f"生成 MinIO 访问 URL 失败：{str(e)}")
        return url