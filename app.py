

# st.divider()
# st.markdown("<div style='text-align:center;color:#666;'><strong>AI Assistant v2.0</strong> | Powered by Groq</div>", unsafe_allow_html=True)
import streamlit as st
import os
from dotenv import load_dotenv
from summarizer import summarize_text, summarize_pdf_cached
from chat_pdf import chat_with_pdf
from utils import read_pdf as read_pdf_util, get_file_hash, truncate_text
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI PDF & Text Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - FIXED COLOR SCHEME
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-size: 1.1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        color: #000000;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
        color: #000000;
    }
    .summary-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        color: #000000;
        line-height: 1.6;
        font-size: 1rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_pdf_hash' not in st.session_state:
    st.session_state.current_pdf_hash = None
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = None
if 'summary_cache' not in st.session_state:
    st.session_state.summary_cache = {}

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # API Key status
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        st.success("✅ API Key Configured")
    else:
        st.error("❌ API Key Not Found")
        st.info("Add GEMINI_API_KEY to your .env file")
    
    st.divider()
    
    # Statistics
    st.subheader("📊 Session Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Summaries", len(st.session_state.summary_cache))
    with col2:
        st.metric("Chat Msgs", len(st.session_state.chat_history))
    
    st.divider()
    
    # Clear buttons
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    if st.button("🗑️ Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.summary_cache = {}
        st.success("Cache cleared!")
    
    st.divider()
    st.caption("Made with ❤️ using Streamlit & Groq")

# Main header
st.markdown('<p class="main-header">📄 AI PDF & Text Assistant</p>', unsafe_allow_html=True)
st.markdown("##### Powered by Groq LLaMA Models | Fast & Intelligent Document Analysis")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📝 Summarize", "💬 Chat with PDF", "ℹ️ Help"])

# ============== TAB 1: SUMMARIZATION ==============
with tab1:
    st.header("📝 Text & PDF Summarization")
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["📝 Text Input", "📄 PDF Upload"],
            horizontal=True
        )
    
    with col2:
        summary_type = st.selectbox(
            "Summary Style:",
            ["concise", "detailed", "bullet"],
            format_func=lambda x: {
                "concise": "🎯 Concise",
                "detailed": "📚 Detailed",
                "bullet": "📋 Bullet Points"
            }[x]
        )
    
    st.divider()
    
    text_to_summarize = ""
    pdf_hash = None
    
    if input_method == "📝 Text Input":
        # Text input
        text_to_summarize = st.text_area(
            "Enter your text:",
            height=300,
            placeholder="Paste your text here... (minimum 50 characters)",
            help="Enter at least 50 characters for meaningful summarization",
            key="text_input_area"
        )
        
        # Live character and word count
        char_count = len(text_to_summarize)
        word_count = len(text_to_summarize.split())
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Characters", f"{char_count:,}")
        with col2:
            st.metric("Words", f"{word_count:,}")
    
    else:
        # PDF upload
        uploaded_file = st.file_uploader(
            "Upload a PDF file:",
            type=["pdf"],
            help="Maximum file size: 200MB",
            key="summary_pdf"
        )
        
        if uploaded_file:
            # Get file info
            file_size = uploaded_file.size / (1024 * 1024)  # MB
            pdf_hash = get_file_hash(uploaded_file)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File Name", truncate_text(uploaded_file.name, 20))
            with col2:
                st.metric("File Size", f"{file_size:.2f} MB")
            with col3:
                st.metric("Status", "✅ Ready")
            
            # Extract text with progress
            with st.spinner("📖 Extracting text from PDF..."):
                text_to_summarize = read_pdf_util(uploaded_file, method='pypdf2')
            
            if text_to_summarize:
                st.success(f"✅ Extracted {len(text_to_summarize.split())} words from PDF")
                
                # Show preview
                with st.expander("📄 Preview extracted text"):
                    st.text_area("First 500 characters:", 
                               text_to_summarize[:500] + "...", 
                               height=150,
                               disabled=True)
    
    st.divider()
    
    # Summarize button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        summarize_button = st.button(
            "🚀 Generate Summary",
            type="primary",
            use_container_width=True
        )
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.rerun()
    
    # Generate summary
    if summarize_button:
        if not text_to_summarize or len(text_to_summarize.strip()) < 50:
            st.warning("⚠️ Please provide at least 50 characters of text to summarize.")
        else:
            # Show character count before processing
            total_chars = len(text_to_summarize)
            total_words = len(text_to_summarize.split())
            
            # Display processing info
            st.info(f"📊 Processing: {total_chars:,} characters | {total_words:,} words")
            
            # Show progress
            with st.spinner("🤖 AI is generating your summary..."):
                start_time = datetime.now()
                
                # Use cached version for PDFs
                if pdf_hash:
                    summary = summarize_pdf_cached(pdf_hash, text_to_summarize, summary_type)
                else:
                    summary = summarize_text(text_to_summarize, summary_type)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
            
            # Display results with stats
            st.success(f"✅ Summary generated in {duration:.2f} seconds | Processed {total_chars:,} characters")
            
            st.subheader("📋 Summary:")
            # Display summary with proper visibility
            if summary and summary.strip():
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4; color: #000000; line-height: 1.6; font-size: 1rem;">
                {summary}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ No summary was generated. Please try again.")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "💾 Download Summary",
                    data=summary,
                    file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.toast("Use Ctrl+C to copy the summary text above!")
            with col3:
                if st.button("🔄 New Summary", use_container_width=True):
                    st.rerun()

# ============== TAB 2: CHAT WITH PDF ==============
with tab2:
    st.header("💬 Chat with Your PDF")
    st.markdown("Upload a PDF and ask questions about its content using AI")
    
    # PDF upload section
    uploaded_pdf = st.file_uploader(
        "📤 Upload PDF Document:",
        type=["pdf"],
        help="Upload a PDF to start chatting",
        key="chat_pdf_uploader"
    )
    
    if uploaded_pdf:
        # Get file hash for caching
        current_hash = get_file_hash(uploaded_pdf)
        
        # Check if new PDF
        if current_hash != st.session_state.current_pdf_hash:
            st.session_state.current_pdf_hash = current_hash
            st.session_state.chat_history = []
            st.session_state.pdf_text = None
        
        # Display PDF info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📄 File", truncate_text(uploaded_pdf.name, 15))
        with col2:
            file_size_mb = uploaded_pdf.size / (1024 * 1024)
            st.metric("📊 Size", f"{file_size_mb:.1f} MB")
        with col3:
            st.metric("💬 Messages", len(st.session_state.chat_history))
        with col4:
            st.metric("🔄 Status", "✅ Ready")
        
        st.divider()
        
        # Chat interface
        st.subheader("💭 Ask Questions")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 📜 Conversation History")
            
            for idx, (question, answer) in enumerate(st.session_state.chat_history):
                # User message
                st.markdown(f"""
                <div class='chat-message user-message'>
                    <strong>🙋 You:</strong><br>{question}
                </div>
                """, unsafe_allow_html=True)
                
                # Assistant message
                st.markdown(f"""
                <div class='chat-message assistant-message'>
                    <strong>🤖 Assistant:</strong><br>{answer}
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
        
        # Question input
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_question = st.text_input(
                "Your question:",
                placeholder="e.g., What is the main topic of this document?",
                key="question_input",
                label_visibility="collapsed"
            )
        
        with col2:
            ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
        
        # Suggested questions
        with st.expander("💡 Suggested Questions"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📌 Summarize this document", use_container_width=True):
                    user_question = "Can you provide a summary of this document?"
                    ask_button = True
                if st.button("🔍 What are the key points?", use_container_width=True):
                    user_question = "What are the key points in this document?"
                    ask_button = True
            with col2:
                if st.button("📊 Main findings?", use_container_width=True):
                    user_question = "What are the main findings or conclusions?"
                    ask_button = True
                if st.button("👥 Who is mentioned?", use_container_width=True):
                    user_question = "Who are the main people or entities mentioned?"
                    ask_button = True
        
        # Process question
        if ask_button and user_question.strip():
            with st.spinner("🤖 Analyzing document and generating answer..."):
                start_time = datetime.now()
                
                # Get answer
                answer, source_docs = chat_with_pdf(
                    uploaded_pdf,
                    user_question,
                    current_hash,
                    st.session_state.chat_history
                )
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
            
            # Add to history
            st.session_state.chat_history.append((user_question, answer))
            
            # Display new answer
            st.success(f"✅ Answer generated in {duration:.2f} seconds")
            
            st.markdown(f"""
            <div class='chat-message user-message'>
                <strong>🙋 You:</strong><br>{user_question}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='chat-message assistant-message'>
                <strong>🤖 Assistant:</strong><br>{answer}
            </div>
            """, unsafe_allow_html=True)
            
            # Show sources if available
            if source_docs:
                with st.expander("📚 View Source Excerpts"):
                    for idx, doc in enumerate(source_docs[:3], 1):
                        st.markdown(f"**Source {idx}:**")
                        st.text(truncate_text(doc.page_content, 200))
                        st.divider()
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Export Chat", key="export_chat", use_container_width=True):
                    chat_export = ""
                    for q, a in st.session_state.chat_history:
                        chat_export += f"Q: {q}\n\nA: {a}\n\n{'='*50}\n\n"
                    
                    st.download_button(
                        "📥 Download Conversation",
                        data=chat_export,
                        file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("🔄 Ask Another", key="ask_another", use_container_width=True):
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Clear Chat", key="clear_chat_btn", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
        
        elif ask_button and not user_question.strip():
            st.warning("⚠️ Please enter a question!")
    
    else:
        # No PDF uploaded
        st.info("👆 Please upload a PDF document to start chatting")
        
        st.markdown("""
        ### 🎯 How it works:
        1. **Upload** a PDF document
        2. **Ask** questions about its content
        3. **Get** AI-powered answers with source references
        4. **Continue** the conversation with follow-up questions
        
        ### ✨ Features:
        - 🧠 Context-aware responses
        - 📚 Source citation
        - 💾 Export conversations
        - 🔄 Conversation history
        """)

# ============== TAB 3: HELP & INFORMATION ==============
with tab3:
    st.header("ℹ️ Help & Information")
    
    st.markdown("""
    ## 🚀 Quick Start Guide
    
    ### Setting Up
    1. **Get API Key**: Sign up at [Groq Console](https://console.groq.com)
    2. **Configure**: Add `GROQ_API_KEY=your_key` to `.env` file
    3. **Install**: Run `pip install -r requirements.txt`
    4. **Launch**: Run `streamlit run app.py`
    
    ---
    
    ## 📝 Summarization Tips
    - Minimum 50 characters for meaningful results
    - Choose summary style based on your needs
    - PDFs are cached for faster repeated use
    
    ## 💬 Chat Tips
    - Be specific in your questions
    - Ask one thing at a time
    - Use suggested questions to start
    - Check source excerpts for accuracy
    
    ## 🐛 Troubleshooting
    
    **API Key Issues:**
    - Ensure `.env` file exists
    - Check spelling: `GROQ_API_KEY=your_key`
    - Restart application after changes
    
    **PDF Reading Problems:**
    - Ensure PDF isn't password-protected
    - Try re-uploading the file
    - Check file isn't corrupted
    
    **Slow Performance:**
    - First query takes longer (builds index)
    - Subsequent queries use cache
    - Clear cache if experiencing issues
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>AI PDF & Text Assistant v2.0</strong></p>
    <p>Powered by Groq LLaMA Models | Built with Streamlit</p>
    <p style='font-size: 0.8rem;'>⚡ Fast • 🎯 Accurate • 🔒 Secure</p>
</div>
""", unsafe_allow_html=True)