
import os
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from PyPDF2 import PdfReader
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini directly
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
else:
    model = None

# OPTIMIZED text splitter - larger chunks = fewer embeddings
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,  # Larger chunks
    chunk_overlap=100,  # Minimal overlap
    length_function=len,
    separators=["\n\n\n", "\n\n", "\n", ". ", " "]
)


def read_pdf(file_path):
    """Extract text from PDF."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""


@st.cache_resource(show_spinner=False)
def create_vectorstore(_file_hash, text):
    """
    Create and cache vectorstore for PDF - OPTIMIZED FOR SPEED.
    Using _file_hash to avoid hashing issues with streamlit cache.
    """
    try:
        # SPEED OPTIMIZATION: Limit text length to prevent slow embedding
        max_chars = 50000  # Process max 50k characters
        if len(text) > max_chars:
            text = text[:max_chars]
            st.info(f"⚡ Processing first 50k characters for optimal speed")
        
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        # SPEED OPTIMIZATION: Limit number of chunks
        max_chunks = 30  # Max 30 chunks for speed
        if len(chunks) > max_chunks:
            chunks = chunks[:max_chunks]
            st.info(f"⚡ Using first {max_chunks} sections for fast processing")
        
        # Create embeddings with lightweight model
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True, 'batch_size': 8}
        )
        
        # Create vectorstore
        vectorstore = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            collection_name=f"pdf_{_file_hash[:8]}"
        )
        
        return vectorstore
        
    except Exception as e:
        st.error(f"Error creating search index: {str(e)}")
        return None


def chat_with_pdf(file_path, query, file_hash, chat_history=None):
    """
    Chat with PDF using direct Gemini API and RAG.
    """
    try:
        if not model:
            return "❌ Gemini API key not configured.", []
            
        # Read PDF
        text = read_pdf(file_path)
        
        if not text or text.strip() == "":
            return "❌ Could not extract text from PDF.", []
        
        # Create or retrieve cached vectorstore
        vectorstore = create_vectorstore(file_hash, text)
        
        if not vectorstore:
            return "❌ Error creating search index.", []
        
        # Get relevant documents
        docs = vectorstore.similarity_search(query, k=3)
        
        if not docs:
            return "❌ No relevant information found in the PDF.", []
        
        # Combine context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create prompt
        prompt = f"""Answer the question based on the context below. If the answer is not in the context, say "Not found in document."

Context:
{context}

Question: {query}

Answer:"""
        
        # Get answer from Gemini
        response = model.generate_content(prompt)
        answer = response.text.strip() if response.text else "No response generated."
        
        return answer, docs
        
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return "⏱️ Request timed out. Please try again.", []
        elif "rate limit" in error_msg.lower():
            return "🚫 Rate limit reached. Wait a moment.", []
        return f"❌ Error: {error_msg}", []


def get_conversation_summary(chat_history):
    """Generate a summary of the conversation."""
    if not chat_history or len(chat_history) == 0:
        return "No conversation yet."
    
    summary = f"Total exchanges: {len(chat_history)}\n\n"
    for idx, (q, a) in enumerate(chat_history[-3:], 1):  # Last 3 exchanges
        summary += f"Q{idx}: {q[:100]}...\n"
    
    return summary