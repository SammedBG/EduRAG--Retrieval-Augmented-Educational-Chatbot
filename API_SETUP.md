# API Setup Guide for High-Accuracy RAG Chatbot

## 🚀 Best Free API Options

### 1. Groq API (RECOMMENDED)
- **Free**: 14,400 requests/day
- **Models**: Llama 3.1 70B, Mixtral 8x7B, Gemma 2 9B
- **Speed**: Extremely fast (100+ tokens/sec)
- **Accuracy**: Very high (comparable to GPT-4)

#### Setup Steps:
1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign up for free account
3. Create a new API key
4. Create a `.env` file in your project root:
```
GROQ_API_KEY=your_actual_api_key_here
```

### 2. Hugging Face API (Alternative)
- **Free**: 1,000 requests/month
- **Models**: Various high-quality models
- **Accuracy**: Good

#### Setup Steps:
1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create a new token
3. Add to your `.env` file:
```
HF_API_TOKEN=your_actual_token_here
```

## 📦 Install Dependencies

```bash
pip install requests python-dotenv
```

## 🎯 Usage

The chatbot will automatically:
1. Try Groq API first (if API key is provided)
2. Fall back to Hugging Face API (if Groq fails)
3. Use local fallback method (if both APIs fail)

## 🔧 Models Available

### Groq Models:
- `llama-3.1-70b-versatile` (Best accuracy)
- `llama-3.1-8b-instant` (Faster)
- `mixtral-8x7b-32768` (Good balance)
- `gemma-7b-it` (Efficient)

### Hugging Face Models:
- `microsoft/DialoGPT-medium`
- `microsoft/DialoGPT-large`
- `facebook/blenderbot-400M-distill`
