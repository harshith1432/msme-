"""
Abstract Storage Provider interface and implementations (Local and S3).
"""
import os
import shutil
import hashlib
from abc import ABC, abstractmethod

class StorageProvider(ABC):
    @abstractmethod
    def upload_file(self, file_obj, object_key, content_type=None) -> str:
        """Uploads a file and returns its stored object key."""
        pass

    @abstractmethod
    def download_file(self, object_key) -> bytes:
        """Retrieves and returns file contents as bytes."""
        pass

    @abstractmethod
    def get_temporary_download_url(self, object_key, expires_in=3600) -> str:
        """Generates a temporary signed or internal download URL."""
        pass

    @abstractmethod
    def delete_file(self, object_key) -> bool:
        """Deletes a file by its object key."""
        pass

    @abstractmethod
    def file_exists(self, object_key) -> bool:
        """Checks if a file exists."""
        pass

    @abstractmethod
    def calculate_checksum(self, object_key) -> str:
        """Calculates SHA-256 checksum of the stored file."""
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider for dev, test, and isolated deployments."""
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        os.makedirs(self.root_dir, exist_ok=True)

    def _get_full_path(self, object_key):
        safe_key = object_key.replace('\\', '/').lstrip('/')
        return os.path.join(self.root_dir, safe_key)

    def upload_file(self, file_obj, object_key, content_type=None) -> str:
        full_path = self._get_full_path(object_key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if hasattr(file_obj, 'read'):
            with open(full_path, 'wb') as f:
                shutil.copyfileobj(file_obj, f)
        elif isinstance(file_obj, (bytes, bytearray)):
            with open(full_path, 'wb') as f:
                f.write(file_obj)
        elif isinstance(file_obj, str) and os.path.exists(file_obj):
            shutil.copy2(file_obj, full_path)
        else:
            raise ValueError("Unsupported file_obj type for upload")
        return object_key

    def download_file(self, object_key) -> bytes:
        full_path = self._get_full_path(object_key)
        with open(full_path, 'rb') as f:
            return f.read()

    def get_temporary_download_url(self, object_key, expires_in=3600) -> str:
        # In local dev/test mode, proxy through the backend vault endpoint
        return f"/vault/download-file?key={object_key}"

    def delete_file(self, object_key) -> bool:
        full_path = self._get_full_path(object_key)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def file_exists(self, object_key) -> bool:
        return os.path.exists(self._get_full_path(object_key))

    def calculate_checksum(self, object_key) -> str:
        full_path = self._get_full_path(object_key)
        hasher = hashlib.sha256()
        with open(full_path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()


class S3StorageProvider(StorageProvider):
    """Production S3-compatible object storage provider (AWS S3, MinIO, Cloudflare R2)."""
    def __init__(self, endpoint_url, access_key, secret_key, default_bucket, region='ap-south-1'):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.default_bucket = default_bucket
        self.region = region
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client(
                    's3',
                    endpoint_url=self.endpoint_url,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region
                )
            except ImportError:
                raise RuntimeError("boto3 is required for S3StorageProvider")
        return self._client

    def upload_file(self, file_obj, object_key, content_type=None) -> str:
        client = self._get_client()
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type

        if hasattr(file_obj, 'read'):
            client.upload_fileobj(file_obj, self.default_bucket, object_key, ExtraArgs=extra_args)
        elif isinstance(file_obj, (bytes, bytearray)):
            client.put_object(Bucket=self.default_bucket, Key=object_key, Body=file_obj, **extra_args)
        elif isinstance(file_obj, str) and os.path.exists(file_obj):
            client.upload_file(file_obj, self.default_bucket, object_key, ExtraArgs=extra_args)
        return object_key

    def download_file(self, object_key) -> bytes:
        client = self._get_client()
        response = client.get_object(Bucket=self.default_bucket, Key=object_key)
        return response['Body'].read()

    def get_temporary_download_url(self, object_key, expires_in=3600) -> str:
        client = self._get_client()
        return client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.default_bucket, 'Key': object_key},
            ExpiresIn=expires_in
        )

    def delete_file(self, object_key) -> bool:
        client = self._get_client()
        client.delete_object(Bucket=self.default_bucket, Key=object_key)
        return True

    def file_exists(self, object_key) -> bool:
        client = self._get_client()
        try:
            client.head_object(Bucket=self.default_bucket, Key=object_key)
            return True
        except Exception:
            return False

    def calculate_checksum(self, object_key) -> str:
        content = self.download_file(object_key)
        return hashlib.sha256(content).hexdigest()


def get_storage_provider(config=None) -> StorageProvider:
    backend = os.environ.get('STORAGE_BACKEND', 'local') if not config else getattr(config, 'STORAGE_BACKEND', 'local')
    if backend == 's3':
        endpoint = os.environ.get('S3_ENDPOINT_URL')
        access_key = os.environ.get('S3_ACCESS_KEY')
        secret_key = os.environ.get('S3_SECRET_KEY')
        bucket = os.environ.get('S3_BUCKET_PRIVATE', 'msme-private-documents')
        region = os.environ.get('S3_REGION', 'ap-south-1')
        return S3StorageProvider(endpoint, access_key, secret_key, bucket, region)
    
    upload_folder = os.environ.get('STORAGE_LOCAL_ROOT') or os.path.join(os.getcwd(), 'uploads')
    return LocalStorageProvider(upload_folder)
