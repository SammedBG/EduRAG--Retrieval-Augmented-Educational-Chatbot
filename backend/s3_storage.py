"""
AWS S3 Storage Handler for RAG Chatbot
Handles file uploads, downloads, and management using AWS S3 free tier
"""

import boto3
import os
from pathlib import Path
from typing import List, Optional
import tempfile
from botocore.exceptions import ClientError, NoCredentialsError

class S3Storage:
    def __init__(self):
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'edurag-chatbot-files')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=self.region
            )
            self.available = True
        except NoCredentialsError:
            print("⚠️ AWS credentials not found. S3 storage disabled.")
            self.available = False
        except Exception as e:
            print(f"⚠️ S3 initialization failed: {e}")
            self.available = False
    
    def upload_file(self, file_content: bytes, filename: str) -> bool:
        """Upload file to S3"""
        if not self.available:
            return False
            
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"course_notes/{filename}",
                Body=file_content,
                ContentType='application/pdf'
            )
            print(f"✅ Uploaded {filename} to S3")
            return True
        except ClientError as e:
            print(f"❌ Failed to upload {filename} to S3: {e}")
            return False
    
    def download_file(self, filename: str) -> Optional[bytes]:
        """Download file from S3"""
        if not self.available:
            return None
            
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=f"course_notes/{filename}"
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"❌ Failed to download {filename} from S3: {e}")
            return None
    
    def list_files(self) -> List[dict]:
        """List all PDF files in S3"""
        if not self.available:
            return []
            
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='course_notes/'
            )
            
            files = []
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.pdf'):
                    filename = obj['Key'].split('/')[-1]
                    files.append({
                        'name': filename,
                        'size': obj['Size'],
                        'uploaded': obj['LastModified'].timestamp()
                    })
            return files
        except ClientError as e:
            print(f"❌ Failed to list files from S3: {e}")
            return []
    
    def delete_file(self, filename: str) -> bool:
        """Delete file from S3"""
        if not self.available:
            return False
            
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=f"course_notes/{filename}"
            )
            print(f"✅ Deleted {filename} from S3")
            return True
        except ClientError as e:
            print(f"❌ Failed to delete {filename} from S3: {e}")
            return False
    
    def download_all_files(self, local_dir: Path) -> List[str]:
        """Download all files from S3 to local directory for processing"""
        if not self.available:
            return []
            
        files = self.list_files()
        downloaded_files = []
        
        for file_info in files:
            filename = file_info['name']
            content = self.download_file(filename)
            if content:
                local_path = local_dir / filename
                with open(local_path, 'wb') as f:
                    f.write(content)
                downloaded_files.append(filename)
                print(f"✅ Downloaded {filename} for processing")
        
        return downloaded_files

# Global S3 instance
s3_storage = S3Storage()
