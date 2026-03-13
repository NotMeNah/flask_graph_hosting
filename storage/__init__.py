import config
from .local import LocalStorage
from .minio import MinioStorage

def get_storage():
    if config.STORAGE_TYPE=="minio":
        return MinioStorage()
    return LocalStorage()