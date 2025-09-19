# 🚀 RAG Chatbot Deployment Guide

Complete guide for deploying your full-stack RAG chatbot with React frontend and FastAPI backend.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

## 🏗️ Project Structure

```
RAG_CHATBOT/
├── backend/                 # FastAPI backend
│   ├── main.py             # API endpoints
│   ├── Dockerfile          # Backend container
│   └── requirements.txt    # Backend dependencies
├── frontend/               # React frontend
│   ├── src/               # React source code
│   ├── public/            # Static files
│   ├── Dockerfile         # Frontend container
│   └── package.json       # Frontend dependencies
├── rag_chatbot/           # Core RAG functionality
├── docker-compose.yml     # Multi-container setup
├── nginx.conf            # Reverse proxy
└── env.example           # Environment variables template
```

## 🚀 Quick Deployment

### 1. Clone and Setup
```bash
git clone <your-repo>
cd RAG_CHATBOT
```

### 2. Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your API keys
nano .env
```

### 3. Deploy with Docker
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Access Your Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Nginx Proxy**: http://localhost:80

## 🔧 Local Development

### Backend Development
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Run backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start
```

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /health` - System status
- `POST /upload` - Upload PDF files
- `POST /chat` - Send chat message
- `GET /files` - List uploaded files
- `DELETE /files/{filename}` - Delete file
- `WebSocket /ws` - Real-time chat

### Example API Usage
```bash
# Upload files
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document.pdf"

# Send chat message
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Parkinson'\''s disease?"}'
```

## 🎯 Features

### Frontend Features
- **File Upload**: Drag & drop PDF upload
- **Real-time Chat**: WebSocket-based chat interface
- **Document Management**: View and delete uploaded files
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Built with React and Tailwind CSS

### Backend Features
- **FastAPI**: High-performance async API
- **File Processing**: Automatic PDF text extraction
- **Vector Search**: FAISS-based document retrieval
- **AI Integration**: Groq and Hugging Face APIs
- **WebSocket Support**: Real-time communication

## 🔐 Security Considerations

### Production Deployment
1. **Environment Variables**: Never commit API keys
2. **HTTPS**: Use SSL certificates in production
3. **CORS**: Configure allowed origins properly
4. **Rate Limiting**: Implement API rate limiting
5. **Authentication**: Add user authentication if needed

### Example Production Setup
```bash
# Use environment variables
export GROQ_API_KEY="your_production_key"
export HF_API_TOKEN="your_production_token"

# Run with production settings
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.scale.yml
services:
  backend:
    deploy:
      replicas: 3
  frontend:
    deploy:
      replicas: 2
```

### Database Integration
For production, consider adding:
- PostgreSQL for user data
- Redis for caching
- Elasticsearch for advanced search

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   
   # Change ports in docker-compose.yml
   ports:
     - "8001:8000"  # Use different port
   ```

2. **Memory Issues**
   ```bash
   # Increase Docker memory limit
   docker-compose up --build --memory=4g
   ```

3. **API Key Issues**
   ```bash
   # Check environment variables
   docker-compose exec backend env | grep API
   ```

### Logs
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View specific service logs
docker-compose logs backend
```

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

### Backup
```bash
# Backup data
docker-compose exec backend tar -czf /tmp/backup.tar.gz /app/data /app/embeddings

# Copy backup
docker cp <container_id>:/tmp/backup.tar.gz ./backup.tar.gz
```

## 📞 Support

For issues and questions:
1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Ensure all services are running: `docker-compose ps`
4. Check API health: `curl http://localhost:8000/health`

## 🎉 Success!

Your RAG chatbot is now deployed and ready to use! Users can:
1. Upload PDF documents through the web interface
2. Chat with their documents using AI-powered responses
3. Get accurate answers based on document content
4. Manage their uploaded files

The system automatically processes documents, creates embeddings, and provides intelligent responses using state-of-the-art language models.
