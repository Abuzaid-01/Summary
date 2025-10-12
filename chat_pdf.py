import os 
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from PyPDF2 import PdfReader


from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    api_key=API_KEY, 
    model="llama-3.1-70b-versatile",
    temperature=0.5,
    max_tokens=1024
)
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chat_with_pdf(file_path, query):
    text = read_pdf(file_path)
    chunks = text_splitter.split_text(text)
    docs = [Document(page_content=chunk) for chunk in chunks]

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  
    vectorstore = Chroma.from_documents(docs, embeddings)
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    
    answer = qa.run(query)
    return answer

