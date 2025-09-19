# AWS S3 Setup for RAG Chatbot

This guide will help you set up AWS S3 for persistent storage of your RAG chatbot documents and embeddings.

## Why AWS S3?

- **Free Tier**: 5GB storage, 20,000 GET requests, 2,000 PUT requests per month for 12 months
- **Persistent**: Files survive server restarts and deployments
- **Scalable**: Can handle large document collections
- **Reliable**: 99.999999999% (11 9's) durability

## Step 1: Create AWS Account

1. Go to [AWS Console](https://aws.amazon.com/)
2. Click "Create an AWS Account"
3. Follow the signup process (requires credit card for verification, but free tier won't charge)

## Step 2: Create S3 Bucket

1. Go to [S3 Console](https://s3.console.aws.amazon.com/)
2. Click "Create bucket"
3. **Bucket name**: Choose a unique name (e.g., `your-name-rag-chatbot-data`)
4. **Region**: Choose `us-east-1` (N. Virginia) for best performance
5. **Block Public Access**: Keep all settings checked (default)
6. Click "Create bucket"

## Step 3: Create IAM User

1. Go to [IAM Console](https://console.aws.amazon.com/iam/)
2. Click "Users" → "Create user"
3. **User name**: `rag-chatbot-s3-user`
4. **Access type**: Check "Programmatic access"
5. Click "Next: Permissions"

### Attach Policy

1. Click "Attach existing policies directly"
2. Search for and select: `AmazonS3FullAccess`
3. Click "Next: Tags" → "Next: Review" → "Create user"

### Save Credentials

1. **IMPORTANT**: Copy and save these values:
   - Access Key ID
   - Secret Access Key
2. Click "Download .csv" to save credentials securely

## Step 4: Configure Environment Variables

### For Local Development

Create a `.env` file in your project root:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name-here

# LLM API Keys
GROQ_API_KEY=your_groq_api_key_here
HF_API_TOKEN=your_huggingface_token_here
```

### For Render Deployment

1. Go to your Render service dashboard
2. Click "Environment" tab
3. Add these environment variables:
   - `AWS_ACCESS_KEY_ID`: Your access key
   - `AWS_SECRET_ACCESS_KEY`: Your secret key
   - `AWS_DEFAULT_REGION`: `us-east-1`
   - `AWS_S3_BUCKET`: Your bucket name

## Step 5: Test the Setup

1. Start your backend:
   ```bash
   cd backend
   python main.py
   ```

2. Upload a PDF file through the frontend
3. Check your S3 bucket - you should see:
   - `data/course_notes/your-file.pdf`
   - `embeddings/vector_index.pkl`

## Step 6: Deploy to Render

1. Push your code to GitHub
2. Connect your repo to Render
3. Use the `render.yaml` configuration
4. Set the environment variables in Render dashboard
5. Deploy!

## Cost Monitoring

- **Free Tier**: 5GB storage, 20,000 GET requests, 2,000 PUT requests/month
- **Beyond Free Tier**: ~$0.023/GB/month for storage
- Monitor usage in [AWS Billing Dashboard](https://console.aws.amazon.com/billing/)

## Security Best Practices

1. **Never commit credentials** to Git
2. **Use IAM policies** with minimal required permissions
3. **Enable MFA** on your AWS account
4. **Monitor access** through CloudTrail
5. **Rotate keys** regularly

## Troubleshooting

### "Access Denied" Error
- Check IAM user has S3 permissions
- Verify bucket name is correct
- Ensure region matches

### "Bucket Not Found" Error
- Verify bucket name spelling
- Check region is correct
- Ensure bucket exists in the right region

### "Invalid Credentials" Error
- Verify Access Key ID and Secret Key
- Check for extra spaces in environment variables
- Ensure credentials are for the correct AWS account

## Alternative: No S3 (Local Only)

If you prefer not to use S3, the app will work in local-only mode:
- Files stored locally on server
- Data lost on server restart
- Good for testing/development

Just don't set the AWS environment variables, and the app will automatically use local storage only.
