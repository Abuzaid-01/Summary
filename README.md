# PDF Text AI Tool

A Streamlit application for text and PDF summarization and chat functionality using Groq's AI models.

## Features

- **Text Summarization**: Summarize any text input or PDF document
- **PDF Chat**: Upload a PDF and ask questions about its content
- **AI-Powered**: Uses Groq's Llama models for fast and accurate responses

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open your browser and go to `http://localhost:8501`
2. Choose between "Summarize Text/PDF" or "Chat with PDF" tabs
3. For summarization: Enter text or upload a PDF file
4. For chat: Upload a PDF and ask questions about its content

## Requirements

- Python 3.8+
- Groq API key (get one from [console.groq.com](https://console.groq.com))

## Project Structure

```
pdf_text_app/
├── app.py              # Main Streamlit application
├── summarizer.py       # Text and PDF summarization logic
├── chat_pdf.py         # PDF chat functionality
├── utils.py            # Helper functions
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in repo)
└── README.md          # This file
```