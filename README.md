# PDF Text AI Tool

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](YOUR_DEPLOYED_APP_URL_HERE)

> 🚀 **[Live Demo](YOUR_DEPLOYED_APP_URL_HERE)** - Try it now!

A powerful Streamlit application for AI-powered text and PDF summarization with interactive chat capabilities using Groq's LLaMA models.

## ✨ Features

- **📝 Text Summarization**: Summarize any text input with multiple style options (concise, detailed, bullet points)
- **📄 PDF Summarization**: Upload and summarize PDF documents automatically
- **💬 PDF Chat**: Interactive Q&A with your PDF documents using RAG (Retrieval Augmented Generation)
- **⚡ Fast Processing**: Optimized for speed with intelligent caching
- **🎯 Smart Caching**: Repeated operations use cache for instant results
- **📊 Live Metrics**: Real-time character and word count tracking

## 🚀 Quick Start

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abuzaid-01/Summary.git
   cd Summary
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key**
   - Get your free API key from [Groq Console](https://console.groq.com)
   - Create a `.env` file in the project root:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open browser**
   - Navigate to `http://localhost:8501`

## ☁️ Deploy to Streamlit Cloud

1. **Fork/Push to GitHub**
   - Ensure your code is on GitHub

2. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub

3. **Deploy**
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Click "Deploy"

4. **Add Secrets**
   - Go to App Settings → Secrets
   - Add:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```

## 📖 Usage Guide

### Summarization
1. Choose input method (Text or PDF)
2. Enter/upload your content
3. Select summary style (concise, detailed, or bullet points)
4. Click "Generate Summary"
5. View and download results

### PDF Chat
1. Upload a PDF document
2. Wait for indexing (first time only)
3. Ask questions about the content
4. Get AI-powered answers with source references
5. Continue conversation with follow-up questions

## 🎯 Performance

- **Text Summarization**: 5-10 seconds
- **PDF Chat (first query)**: 10-15 seconds (builds index)
- **PDF Chat (follow-up)**: 5-8 seconds (uses cache)

*Note: First run may be slower as it downloads AI models*

## 📋 Requirements

- Python 3.8 or higher
- Groq API key (free tier available)
- 2GB RAM minimum
- Internet connection for API calls

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **LLM**: Groq LLaMA 3.1 (8B Instant)
- **Embeddings**: HuggingFace Sentence Transformers
- **Vector Store**: ChromaDB
- **PDF Processing**: PyPDF2
- **Framework**: LangChain

## 📁 Project Structure

```
pdf_text_app/
├── app.py              # Main Streamlit application
├── summarizer.py       # Text/PDF summarization logic
├── chat_pdf.py         # PDF chat functionality
├── utils.py            # Helper functions
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in repo)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## 🔒 Security

- ✅ API keys stored in `.env` (gitignored)
- ✅ Secrets managed via Streamlit Cloud
- ✅ No sensitive data in repository
- ⚠️ Never commit API keys to GitHub

## 🐛 Troubleshooting

### "API Key Not Found"
- Check `.env` file exists with correct format
- Verify `GROQ_API_KEY` is set correctly
- Restart the application

### Slow Performance
- First run downloads models (one-time)
- Check internet connection
- Verify Groq API status

### PDF Upload Fails
- Ensure PDF is not password-protected
- Check file size (< 200MB recommended)
- Try a different PDF

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Abuzaid**
- GitHub: [@Abuzaid-01](https://github.com/Abuzaid-01)

## 🙏 Acknowledgments

- [Groq](https://groq.com) for providing fast LLM inference
- [Streamlit](https://streamlit.io) for the amazing framework
- [LangChain](https://langchain.com) for RAG capabilities

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/Abuzaid-01/Summary/issues)
- Star ⭐ the repo if you find it useful!

---

Made with ❤️ using Streamlit & Groq