# # from PyPDF2 import PdfReader

# # def read_pdf(file):
# #     pdf = PdfReader(file)
# #     text = ""
# #     for page in pdf.pages:
# #         text += page.extract_text() + "\n"
# #     return text


# from PyPDF2 import PdfReader
# import re


# def read_pdf(file):
#     """Extract text from PDF file with better formatting."""
#     try:
#         pdf = PdfReader(file)
#         text = ""
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#         return text.strip()
#     except Exception as e:
#         raise Exception(f"Failed to read PDF: {str(e)}")


# def analyze_document_structure(text):
#     """
#     Analyze document to determine optimal chunking strategy.
#     Returns recommended chunk_size and chunk_overlap.
#     """
#     text_length = len(text)
    
#     # Count structural elements
#     paragraphs = len([p for p in text.split('\n\n') if p.strip()])
#     sentences = len(re.findall(r'[.!?]+', text))
#     avg_paragraph_length = text_length / max(paragraphs, 1)
    
#     # Detect document type and recommend chunking
#     if text_length < 1000:
#         # Very short document
#         return {
#             'chunk_size': text_length,
#             'chunk_overlap': 0,
#             'strategy': 'single_chunk',
#             'reason': 'Document is short enough to process as one chunk'
#         }
    
#     elif text_length < 5000:
#         # Short document
#         return {
#             'chunk_size': 1500,
#             'chunk_overlap': 150,
#             'strategy': 'small_chunks',
#             'reason': 'Short document with moderate chunking'
#         }
    
#     elif avg_paragraph_length > 500:
#         # Long paragraphs (academic/technical)
#         return {
#             'chunk_size': 2000,
#             'chunk_overlap': 300,
#             'strategy': 'large_overlap',
#             'reason': 'Long paragraphs detected - using larger overlap to maintain context'
#         }
    
#     elif paragraphs > 50 and avg_paragraph_length < 200:
#         # Many short paragraphs (articles/reports)
#         return {
#             'chunk_size': 1200,
#             'chunk_overlap': 100,
#             'strategy': 'paragraph_aligned',
#             'reason': 'Many short paragraphs - using smaller chunks'
#         }
    
#     else:
#         # Standard document
#         return {
#             'chunk_size': 1500,
#             'chunk_overlap': 200,
#             'strategy': 'balanced',
#             'reason': 'Standard chunking for balanced performance'
#         }


# def estimate_processing_time(text_length, operation='summarize'):
#     """Estimate processing time for user feedback."""
#     if operation == 'summarize':
#         # Rough estimate: ~500 chars per second
#         seconds = text_length / 500
#     else:  # chat/embed
#         # Embedding is faster
#         seconds = text_length / 1000
    
#     if seconds < 5:
#         return "a few seconds"
#     elif seconds < 30:
#         return "about 30 seconds"
#     elif seconds < 60:
#         return "about a minute"
#     else:
#         return f"about {int(seconds/60)} minutes"


# def clean_text(text):
#     """Clean and normalize text for better processing."""
#     # Remove excessive whitespace
#     text = re.sub(r'\s+', ' ', text)
#     # Remove page numbers (common pattern)
#     text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
#     # Fix common OCR issues
#     text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
#     return text.strip()
import hashlib
from PyPDF2 import PdfReader
import pdfplumber
import streamlit as st
from datetime import datetime

def read_pdf(file, method='pypdf2'):
    """
    Read PDF with fallback options for better text extraction.
    
    Args:
        file: File object
        method: 'pypdf2' or 'pdfplumber'
    
    Returns:
        Extracted text string
    """
    try:
        text = ""
        
        if method == 'pdfplumber':
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        else:
            pdf = PdfReader(file)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text.strip()
    
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""


def get_file_hash(file):
    """Generate hash for file to use in caching."""
    file.seek(0)
    file_hash = hashlib.md5(file.read()).hexdigest()
    file.seek(0)
    return file_hash


def count_tokens(text):
    """Estimate token count (rough approximation)."""
    return len(text.split()) * 1.3


def format_timestamp():
    """Get formatted timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clean_text(text):
    """Clean extracted text."""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    # Remove special characters if needed
    return text


def truncate_text(text, max_length=150):
    """Truncate text for display."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def validate_api_key(api_key):
    """Validate API key format."""
    if not api_key:
        return False, "API key is empty"
    if len(api_key) < 20:
        return False, "API key seems too short"
    return True, "Valid"