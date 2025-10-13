# import os 
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain_core.documents import Document
# from langchain_text_splitters import CharacterTextSplitter
# from langchain_groq import ChatGroq
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain.chains import RetrievalQA
# from PyPDF2 import PdfReader


# from dotenv import load_dotenv
# load_dotenv()


# API_KEY = os.getenv("GROQ_API_KEY")

# llm = ChatGroq(
#     api_key=API_KEY, 
#     model="llama-3.1-70b-versatile",
#     temperature=0.5,
#     max_tokens=1024
# )
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

# def read_pdf(file_path):
#     reader = PdfReader(file_path)
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text() + "\n"
#     return text


# def chat_with_pdf(file_path, query):
#     text = read_pdf(file_path)
#     chunks = text_splitter.split_text(text)
#     docs = [Document(page_content=chunk) for chunk in chunks]

#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  
#     vectorstore = Chroma.from_documents(docs, embeddings)
    
#     qa = RetrievalQA.from_chain_type(
#         llm=llm,
#         chain_type="stuff",
#         retriever=vectorstore.as_retriever()
#     )
    
#     answer = qa.run(query)
#     return answer


import os
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from PyPDF2 import PdfReader
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

# Initialize LLM with SPEED-OPTIMIZED settings
llm = ChatGroq(
    api_key=API_KEY, 
    model="llama-3.1-8b-instant",  # Fastest model
    temperature=0.2,  # Lower for consistency and speed
    max_tokens=400,  # Shorter responses = faster
    timeout=15,  # Shorter timeout
    streaming=False
)

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
    SPEED-OPTIMIZED chat with PDF using RAG.
    
    Args:
        file_path: Path to PDF file
        query: User question
        file_hash: Hash of file for caching
        chat_history: Previous conversation history
    
    Returns:
        Answer string and source documents
    """
    try:
        # Read PDF (cached by Streamlit file uploader)
        text = read_pdf(file_path)
        
        if not text or text.strip() == "":
            return "❌ Could not extract text from PDF.", []
        
        # Create or retrieve cached vectorstore (FAST - cached after first use)
        vectorstore = create_vectorstore(file_hash, text)
        
        if not vectorstore:
            return "❌ Error creating search index.", []
        
        # Create retriever with SPEED optimization
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}  # Reduced from 4 to 3 for speed
        )
        
        # ULTRA-CONCISE prompt for speed
        prompt_template = """Answer briefly based on the context. If not found, say "Not in document."

Context: {context}

Question: {question}

Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # Fastest chain type
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        # Get answer using invoke (modern API)
        result = qa.invoke({"query": query})
        answer = result['result']
        source_docs = result.get('source_documents', [])
        
        return answer, source_docs
        
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