from urllib.parse import urlparse

from minio import Minio
from loguru import logger

from util.decorator import singleton
from ext.ext_oss.provider.base import OssBase


@singleton(
    key_generator=lambda **kwargs: f"{kwargs.get('endpoint', '')}:{kwargs.get('bucket_name', '')}:{kwargs.get('access_key_id', '')}",  # type: ignore
)
class MinioOss(
    OssBase,
):

    client: Minio

    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        endpoint: str,
        external_endpoint: str,
        bucket_name: str,
        cname: bool,
        expire_time: int,
    ):
        """

        Args:
            custom_config (dict):
                access_key: str
                secret_key: str
                bucket_name: str
                endpoint: str
        """
        # 不携带协议前缀
        self.client = Minio(
            endpoint=urlparse(endpoint).netloc if endpoint.startswith("http") else endpoint,
            access_key=access_key_id,
            secret_key=access_key_secret,
            secure=False,
        )
        # if not self.client.bucket_exists(bucket_name): # type: ignore
        # raise RuntimeError(f"bucket: {bucket_name} not exist, create bucket first")
        # logger.warning(f"bucket: {bucket_name} not exist, need create bucket first")
        self.bucket_name = bucket_name
        self.expire_time = expire_time

    def upload(self, file_path: str, object_name: str) -> str:
        """上传文件到 Minio 对象存储."""
        self.client.fput_object(self.bucket_name, object_name, file_path)  # type: ignore
        return f"{self.client._endpoint_url}/{self.bucket_name}/{object_name}"  # type: ignore

    def download(self, object_name: str, file_path: str) -> None:
        """下载文件从 Minio 对象存储."""
        self.client.fget_object(self.bucket_name, object_name, file_path)  # type: ignore

    def delete(self, object_name: str) -> None:
        """删除文件从 Minio 对象存储."""
        self.client.remove_object(self.bucket_name, object_name)  # type: ignore

    def get_presigned_url(self, object_name: str) -> str:
        """获取文件的预签名 URL."""
        return self.client.presigned_get_object(self.bucket_name, object_name, expires=self.expire_time)  # type: ignore
