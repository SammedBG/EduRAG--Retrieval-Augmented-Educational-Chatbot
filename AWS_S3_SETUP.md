# AWS S3 Setup Guide for RAG Chatbot

## 🎯 **Why AWS S3?**
- **Free Tier**: 5GB storage, 20,000 GET requests, 2,000 PUT requests per month
- **Persistent Storage**: Files survive server restarts
- **Scalable**: Can handle unlimited files
- **Reliable**: 99.999999999% durability

## 📋 **Step-by-Step Setup**

### 1. **Create AWS Account**
1. Go to https://aws.amazon.com
2. Click "Create an AWS Account"
3. Follow the signup process
4. **Important**: Use a credit card (won't be charged for free tier usage)

### 2. **Create S3 Bucket**
1. Go to AWS Console → S3
2. Click "Create bucket"
3. **Bucket name**: `edurag-chatbot-files` (must be globally unique)
4. **Region**: `US East (N. Virginia) us-east-1`
5. **Block Public Access**: Keep all settings enabled (default)
6. Click "Create bucket"

### 3. **Create IAM User for API Access**
1. Go to AWS Console → IAM
2. Click "Users" → "Create user"
3. **Username**: `edurag-chatbot-s3-user`
4. **Access type**: "Programmatic access"
5. Click "Next: Permissions"

### 4. **Attach S3 Policy**
1. Click "Attach existing policies directly"
2. Search for "S3" and select:
   - `AmazonS3FullAccess` (for simplicity)
   - OR create custom policy (see below for security)

### 5. **Create Access Keys**
1. Click "Next: Tags" → "Next: Review" → "Create user"
2. **IMPORTANT**: Copy the Access Key ID and Secret Access Key
3. Download the CSV file (you won't see the secret key again!)

## 🔐 **Custom S3 Policy (More Secure)**

Instead of `AmazonS3FullAccess`, create a custom policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::edurag-chatbot-files",
                "arn:aws:s3:::edurag-chatbot-files/*"
            ]
        }
    ]
}
```

## ⚙️ **Configure Render Environment Variables**

In your Render dashboard, add these environment variables:

```
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_S3_BUCKET_NAME=edurag-chatbot-files
AWS_REGION=us-east-1
```

## 🧪 **Test the Setup**

### 1. **Deploy to Render**
```bash
git add .
git commit -m "Add AWS S3 storage integration"
git push
```

### 2. **Check Render Logs**
- Look for: `✅ S3 storage initialized successfully`
- If you see: `⚠️ AWS credentials not found` → Check environment variables

### 3. **Test File Upload**
- Go to your frontend
- Upload a PDF file
- Check if it appears in your S3 bucket

## 💰 **Cost Monitoring**

### Free Tier Limits:
- **Storage**: 5GB
- **Requests**: 20,000 GET + 2,000 PUT per month
- **Duration**: 12 months from signup

### Monitor Usage:
1. Go to AWS Console → Billing
2. Set up billing alerts
3. Monitor S3 usage

## 🔧 **Troubleshooting**

### Common Issues:

1. **"Access Denied"**
   - Check IAM user permissions
   - Verify bucket name matches environment variable

2. **"Bucket not found"**
   - Check bucket name spelling
   - Verify region is correct

3. **"Invalid credentials"**
   - Check Access Key ID and Secret Access Key
   - Ensure no extra spaces in environment variables

### Test S3 Connection:
```python
import boto3
import os

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

# Test connection
try:
    s3.list_buckets()
    print("✅ S3 connection successful!")
except Exception as e:
    print(f"❌ S3 connection failed: {e}")
```

## 🎉 **Expected Results**

After setup:
- ✅ Files upload to S3 instead of local storage
- ✅ Files persist across server restarts
- ✅ No more "no storage" errors
- ✅ Scalable file storage
- ✅ Free tier usage (within limits)

## 📊 **Storage Workflow**

1. **Upload**: File → S3 bucket
2. **Process**: Download from S3 → Process locally → Create embeddings
3. **Query**: Use embeddings to answer questions
4. **List**: Show files from S3
5. **Delete**: Remove from S3

This setup gives you persistent, scalable storage for your RAG chatbot! 🚀
