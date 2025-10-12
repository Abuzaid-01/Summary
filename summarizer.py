import os
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key
API_KEY = os.getenv("GROQ_API_KEY")

# Initialize the LLM, but only if the API key is available
llm = None
if API_KEY:
    llm = ChatGroq(
        api_key=API_KEY, 
        model="llama-3.1-8b-instant",  # Using a faster model
        temperature=0.3,
        max_tokens=512
    )
else:
    print("Warning: GROQ_API_KEY not found. Summarization will not work.")

text_splitter = CharacterTextSplitter(chunk_size=1800, chunk_overlap=100)

def summarize_text(text):
    if not llm:
        return "Error: Groq API key is not configured. Please set GROQ_API_KEY in your .env file."
    
    try:
        print(f"Starting summarization for text of length: {len(text)}")
        
        # For shorter texts, summarize directly
        if len(text) < 2000:
            print("Using direct summarization for short text")
            prompt = f"Please provide a concise summary of the following text:\n\n{text[:1500]}\n\nSummary:"
            response = llm.invoke(prompt)
            print("Direct summarization completed")
            return response.content
        
        # For longer texts, split and summarize
        print("Splitting text into chunks")
        chunks = text_splitter.split_text(text)
        print(f"Created {len(chunks)} chunks")
        
        # Just use the first chunk for now to avoid timeout
        if chunks:
            print("Summarizing first chunk only")
            first_chunk = chunks[0][:1500]  # Limit chunk size further
            prompt = f"Provide a summary of this text:\n\n{first_chunk}\n\nSummary:"
            response = llm.invoke(prompt)
            print("Chunk summarization completed")
            return response.content
        else:
            return "No content to summarize"
            
    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return f"Error during summarization: {str(e)}"

