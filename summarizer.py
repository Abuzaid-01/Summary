


import os
import hashlib
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini directly (not through LangChain)
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
else:
    model = None

# Aggressive text splitter - process LESS text
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=6000,  # Even larger chunks = fewer calls
    chunk_overlap=50,  # Minimal overlap
    length_function=len,
    separators=["\n\n\n", "\n\n", "\n", ". ", " "]
)


# Disable cache temporarily to debug
# @st.cache_data(show_spinner=False, ttl=3600)
def summarize_text(text, summary_type="concise"):
    """
    Summarization using Gemini 2.5 Flash.
    """
    if not model:
        return "❌ Error: Gemini API key not configured."
    
    if not text or text.strip() == "":
        return "❌ No text provided."
    
    try:
        # Better prompts for Gemini
        prompts = {
            "bullet": "Please provide a bullet-point summary of the following text:\n\n{text}\n\nBullet points:",
            "detailed": "Please provide a detailed summary of the following text:\n\n{text}\n\nDetailed summary:",
            "concise": "Please provide a concise summary of the following text:\n\n{text}\n\nSummary:"
        }
        
        template = prompts.get(summary_type, prompts["concise"])
        
        # SPEED OPTIMIZATION 1: Truncate very long texts immediately
        max_input_length = 5000  # Process max 5k chars for speed
        
        if len(text) > max_input_length:
            st.warning(f"⚡ Text truncated to {max_input_length} chars for speed.")
            text = text[:max_input_length]
        
        # Direct Gemini API call
        prompt = template.format(text=text)
        print(f"DEBUG: Sending prompt of length {len(prompt)}")
        
        response = model.generate_content(prompt)
        print(f"DEBUG: Response: {response}")
        print(f"DEBUG: Response text: {repr(response.text)}")
        
        result = response.text.strip() if response.text else ""
        print(f"DEBUG: Final result: {repr(result)}")
        
        if not result:
            return "❌ Empty response from Gemini API"
        return result
        
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return "⏱️ Timeout. Try shorter text."
        elif "rate limit" in error_msg.lower():
            return "🚫 Rate limit. Wait and retry."
        return f"❌ Error: {error_msg}"


# Disable cache temporarily
# @st.cache_data(show_spinner=False, ttl=3600)
def summarize_pdf_cached(pdf_hash, text, summary_type):
    """Cached PDF summarization."""
    return summarize_text(text, summary_type)


