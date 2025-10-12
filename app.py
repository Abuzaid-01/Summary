import streamlit as st
from summarizer import summarize_text
from chat_pdf import chat_with_pdf, read_pdf

st.set_page_config(page_title="Text & PDF AI Tool", layout="wide")
st.title("📄 AI Text & PDF Tool")

# Tabs for modes
tab1, tab2 = st.tabs(["Summarize Text / PDF", "Chat with PDF"])

# Summarize Tab
with tab1:
    st.header("Summarize Text or PDF")
    input_text = st.text_area("Enter text to summarize", height=200)
    uploaded_file = st.file_uploader("Or upload a PDF", type=["pdf"])

    if st.button("Summarize"):
        if uploaded_file:
            text = read_pdf(uploaded_file)
        else:
            text = input_text

        if text.strip() == "":
            st.warning("Please enter text or upload a PDF!")
        else:
            with st.spinner("Generating summary..."):
                summary = summarize_text(text)
            st.subheader("Summary:")
            st.write(summary)

# Chat with PDF Tab 
with tab2:
    st.header("Chat with your PDF")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"], key="chat_pdf")
    user_query = st.text_input("Ask a question about the PDF:")

    if st.button("Get Answer"):
        if uploaded_pdf and user_query.strip() != "":
            with st.spinner("Fetching answer..."):
                answer = chat_with_pdf(uploaded_pdf, user_query)
            st.subheader("Answer:")
            st.write(answer)
        else:
            st.warning("Upload a PDF and type a question!")
