"""
AWS S3 storage integration for persistent file storage
"""

import boto3
import os
import pickle
from pathlib import Path
from typing import List, Optional
import tempfile

class S3Storage:
    def __init__(self):
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        if not all([self.bucket_name, self.aws_access_key, self.aws_secret_key]):
            self.s3_client = None
            print("AWS S3 credentials not configured. Using local storage only.")
        else:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            print(f"S3 storage initialized with bucket: {self.bucket_name}")

    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """Upload a file to S3"""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            print(f"Uploaded {local_path} to s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            print(f"Failed to upload {local_path}: {e}")
            return False

    def download_file(self, s3_key: str, local_path: str) -> bool:
        """Download a file from S3"""
        if not self.s3_client:
            return False
        
        try:
            # Create directory if it doesn't exist
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            print(f"Downloaded s3://{self.bucket_name}/{s3_key} to {local_path}")
            return True
        except Exception as e:
            print(f"Failed to download {s3_key}: {e}")
            return False

    def list_files(self, prefix: str = "") -> List[str]:
        """List files in S3 with given prefix"""
        if not self.s3_client:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            print(f"Failed to list files: {e}")
            return []

    def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3"""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            print(f"Deleted s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            print(f"Failed to delete {s3_key}: {e}")
            return False

    def sync_local_to_s3(self, local_dir: str, s3_prefix: str) -> None:
        """Sync local directory to S3 (memory optimized)"""
        if not self.s3_client:
            return
        
        local_path = Path(local_dir)
        if not local_path.exists():
            return
        
        # Only sync essential files to save memory
        essential_files = ['*.pdf', '*.pkl']
        for pattern in essential_files:
            for file_path in local_path.rglob(pattern):
                if file_path.is_file() and file_path.stat().st_size < 50 * 1024 * 1024:  # < 50MB
                    relative_path = file_path.relative_to(local_path)
                    s3_key = f"{s3_prefix}/{relative_path}".replace('\\', '/')
                    self.upload_file(str(file_path), s3_key)

    def sync_s3_to_local(self, s3_prefix: str, local_dir: str) -> None:
        """Sync S3 directory to local"""
        if not self.s3_client:
            return
        
        files = self.list_files(s3_prefix)
        for s3_key in files:
            relative_path = s3_key[len(s3_prefix):].lstrip('/')
            local_path = Path(local_dir) / relative_path
            self.download_file(s3_key, str(local_path))

    def save_embeddings(self, embeddings_data, s3_key: str = "embeddings/vector_index.pkl") -> bool:
        """Save embeddings to S3"""
        if not self.s3_client:
            return False
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
                pickle.dump(embeddings_data, tmp_file)
                tmp_file.flush()
                
                success = self.upload_file(tmp_file.name, s3_key)
                os.unlink(tmp_file.name)  # Clean up temp file
                return success
        except Exception as e:
            print(f"Failed to save embeddings: {e}")
            return False

    def load_embeddings(self, s3_key: str = "embeddings/vector_index.pkl") -> Optional[any]:
        """Load embeddings from S3"""
        if not self.s3_client:
            return None
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
                if self.download_file(s3_key, tmp_file.name):
                    with open(tmp_file.name, 'rb') as f:
                        embeddings_data = pickle.load(f)
                    os.unlink(tmp_file.name)  # Clean up temp file
                    return embeddings_data
        except Exception as e:
            print(f"Failed to load embeddings: {e}")
        
        return None

# Global S3 storage instance
s3_storage = S3Storage()
