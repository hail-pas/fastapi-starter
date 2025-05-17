from config.default import InstanceExtensionConfig
from ext.ext_oss.provider.base import OssBase
from typing import Literal

class OssConfig(InstanceExtensionConfig[OssBase]):
    provider: Literal["aliyun", "huaweiyun", "minio"] = "aliyun"
    access_key_id: str
    access_key_secret: str
    endpoint: str
    external_endpoint: str = ""
    cname: bool = False
    bucket_name: str
    expire_time: int = 3600 * 24 * 30  # 30天

    def instance(self) -> OssBase:
        provider_cls: OssBase = None

        match self.provider:
            case "aliyun":
                from ext.ext_oss.provider.aliyun import AliyunOss

                provider_cls = AliyunOss
            case "huaweiyun":
                from ext.ext_oss.provider.huaweiyun import HuaweiyunOss

                provider_cls = HuaweiyunOss
            case "minio":
                from ext.ext_oss.provider.aminio import MinioOss

                provider_cls = MinioOss
        return provider_cls(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            endpoint=self.endpoint,
            external_endpoint=self.external_endpoint,
            bucket_name=self.bucket_name,
            cname=self.cname,
            expire_time=self.expire_time,
        )
