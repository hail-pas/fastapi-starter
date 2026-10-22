import abc
import time
import random
import posixpath

from util.general import generate_random_string


class OssBase(abc.ABC):

    @abc.abstractmethod
    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        endpoint: str,
        external_endpoint: str,
        bucket_name: str,
        cname: bool,
        expire_time: int,
    ) -> None: ...

    def get_real_path(
        self,
        filepath: str,
        base_path: str | None = None,
    ) -> str:
        prefix = base_path if base_path else ""
        if not filepath.startswith("/"):
            prefix += "/"
        return f"{prefix}{filepath}"

    @staticmethod
    def get_random_filename(filename: str) -> str:
        random_str = list("pity")
        random.shuffle(random_str)
        return f"{time.time_ns()}_{generate_random_string(4)}_{filename}"

    @abc.abstractmethod
    def create_file(
        self,
        *args,
        **kwargs,
    ) -> tuple[bool, str]:
        """内容上传创建文件"""
        raise NotImplementedError

    @abc.abstractmethod
    def create_file_from_local(
        self,
        *args,
        **kwargs,
    ) -> tuple[bool, str]:
        """上传本地文件"""
        raise NotImplementedError

    @abc.abstractmethod
    def exists(
        self,
        *args,
        **kwargs,
    ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def delete_file(
        self,
        *args,
        **kwargs,
    ) -> tuple[bool, str]:
        """删除文件"""
        raise NotImplementedError

    @abc.abstractmethod
    def download_file(
        self,
        *args,
        **kwargs,
    ) -> tuple[bool, str]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_file_object(
        self,
        *args,
        **kwargs,
    ) -> tuple[bool, bytes | str]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_download_url(
        self,
        *args,
        **kwargs,
    ) -> tuple[bool, str] | tuple[bool, tuple[str, dict] | str]:
        """获取下载url"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_perm_download_url(
        self,
        *args,
        **kwargs,
    ) -> tuple[bool, str] | tuple[bool, tuple[str, dict] | str]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_upload_url(
        self,
        *args,
        **kwargs,
    ) -> tuple[bool, str] | tuple[bool, tuple[str, dict] | str]:
        """获取上传url"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_full_path(
        self,
        filepath: str,
        expires: int | None = None,
    ) -> tuple[bool, str]:
        raise NotImplementedError

    @abc.abstractmethod
    def list_keys(self, prefix: str, max_keys: int = 1000) -> list[str]:
        raise NotImplementedError


def normalize_url(url: str) -> str:
    if not url.startswith("http://") and not url.startswith(
        "https://",
    ):  # noqa
        return "https://" + url
    return url


def clean_path(name: str) -> str:
    """
    Cleans the path so that Windows style paths work
    """
    # Normalize Windows style paths
    clean_name = posixpath.normpath(name).replace("\\", "/")

    # os.path.normpath() can strip trailing slashes so we implement
    # a workaround here.
    if name.endswith("/") and not clean_name.endswith("/"):
        # Add a trailing slash as it was stripped.
        return clean_name + "/"
    return clean_name
