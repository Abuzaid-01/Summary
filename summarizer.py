# import os
# from langchain_core.documents import Document
# from langchain_text_splitters import CharacterTextSplitter
# from langchain_groq import ChatGroq
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Get the API key
# API_KEY = os.getenv("GROQ_API_KEY")

# # Initialize the LLM, but only if the API key is available
# llm = None
# if API_KEY:
#     llm = ChatGroq(
#         api_key=API_KEY, 
#         model="llama-3.1-8b-instant",  # Using a faster model
#         temperature=0.3,
#         max_tokens=512
#     )
# else:
#     print("Warning: GROQ_API_KEY not found. Summarization will not work.")

# text_splitter = CharacterTextSplitter(chunk_size=1800, chunk_overlap=100)

# def summarize_text(text):
#     if not llm:
#         return "Error: Groq API key is not configured. Please set GROQ_API_KEY in your .env file."
    
#     try:
#         print(f"Starting summarization for text of length: {len(text)}")
        
#         # For shorter texts, summarize directly
#         if len(text) < 2000:
#             print("Using direct summarization for short text")
#             prompt = f"Please provide a concise summary of the following text:\n\n{text[:1500]}\n\nSummary:"
#             response = llm.invoke(prompt)
#             print("Direct summarization completed")
#             return response.content
        
#         # For longer texts, split and summarize
#         print("Splitting text into chunks")
#         chunks = text_splitter.split_text(text)
#         print(f"Created {len(chunks)} chunks")
        
#         # Just use the first chunk for now to avoid timeout
#         if chunks:
#             print("Summarizing first chunk only")
#             first_chunk = chunks[0][:1500]  # Limit chunk size further
#             prompt = f"Provide a summary of this text:\n\n{first_chunk}\n\nSummary:"
#             response = llm.invoke(prompt)
#             print("Chunk summarization completed")
#             return response.content
#         else:
#             return "No content to summarize"
            
#     except Exception as e:
#         print(f"Error in summarization: {str(e)}")
#         return f"Error during summarization: {str(e)}"


import os
import hashlib
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

# Initialize LLM with MOST AGGRESSIVE speed settings
llm = None
if API_KEY:
    llm = ChatGroq(
        api_key=API_KEY, 
        model="llama-3.1-8b-instant",  # Fastest Groq model
        temperature=0.1,  # Minimal variation = faster
        max_tokens=300,  # Very short responses = faster
        timeout=15,  # Shorter timeout
        streaming=False
    )

# Aggressive text splitter - process LESS text
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=6000,  # Even larger chunks = fewer calls
    chunk_overlap=50,  # Minimal overlap
    length_function=len,
    separators=["\n\n\n", "\n\n", "\n", ". ", " "]
)


@st.cache_data(show_spinner=False, ttl=3600)
def summarize_text(text, summary_type="concise"):
    """
    ULTRA-FAST summarization - sacrifices completeness for speed.
    """
    if not llm:
        return "❌ Error: Groq API key not configured."
    
    if not text or text.strip() == "":
        return "❌ No text provided."
    
    try:
        # Ultra-short prompts
        prompts = {
            "bullet": "Key points:\n{text}",
            "detailed": "Summarize:\n{text}",
            "concise": "Main idea:\n{text}"
        }
        
        template = prompts.get(summary_type, prompts["concise"])
        
        # SPEED OPTIMIZATION 1: Truncate very long texts immediately
        max_input_length = 5000  # Process max 5k chars for speed
        
        if len(text) > max_input_length:
            st.warning(f"⚡ Text truncated to {max_input_length} chars for speed. Use 'concise' for best results.")
            text = text[:max_input_length]
        
        # SPEED OPTIMIZATION 2: Single API call for everything
        if len(text) < 6000:
            # Direct summarization - FASTEST path
            prompt = template.format(text=text)
            response = llm.invoke(prompt)
            return response.content.strip()
        
        # SPEED OPTIMIZATION 3: Only process 2 chunks maximum
        chunks = text_splitter.split_text(text)[:2]
        
        if len(chunks) == 1:
            prompt = template.format(text=chunks[0])
            response = llm.invoke(prompt)
            return response.content.strip()
        
        # Process 2 chunks only
        st.info("⚡ Processing 2 sections for optimal speed...")
        
        summaries = []
        for idx, chunk in enumerate(chunks):
            # Ultra-minimal prompt
            response = llm.invoke(f"Summarize:\n{chunk[:5000]}")
            summaries.append(response.content.strip())
        
        # Quick combination
        combined = " ".join(summaries)
        final_response = llm.invoke(f"Combine these: {combined}")
        
        return final_response.content.strip()
        
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return "⏱️ Timeout. Try shorter text."
        elif "rate limit" in error_msg.lower():
            return "🚫 Rate limit. Wait and retry."
        return f"❌ Error: {error_msg}"


@st.cache_data(show_spinner=False, ttl=3600)
def summarize_pdf_cached(pdf_hash, text, summary_type):
    """Cached PDF summarization."""
    return summarize_text(text, summary_type)


