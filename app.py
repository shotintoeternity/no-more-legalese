import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Optional: Install these packages if not already available.
# pip install PyPDF2 python-docx python-dotenv

import PyPDF2
import docx

def read_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def read_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error reading DOC/DOCX: {e}")
        return ""

def analyze_document(legal_text):
    prompt = (
        "Please summarize the following legal document. "
        "Explain its overall structure and content, highlight the most important parts, "
        "and analyze whether there is anything anomalous compared to most other legal contracts. "
        "Document:\n\n" + legal_text
    )
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def ask_followup(legal_text, followup_question):
    prompt = (
        "Below is the legal document that was previously analyzed:\n\n"
        f"{legal_text}\n\n"
        "User follow-up question: " + followup_question
    )
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def submit_followup():
    # Triggered when the follow-up input changes (on pressing Enter).
    question = st.session_state.followup_input.strip()
    if question != "":
        with st.spinner("Processing your follow-up question..."):
            answer = ask_followup(st.session_state.legal_text, question)
        st.session_state.followups.append({"question": question, "answer": answer})
        st.session_state.followup_input = ""
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()

def main():
    st.title("No More Legalese")
    st.write("Upload a PDF, DOC/DOCX, or TXT file for analysis.")

    # Initialize session state variables.
    if "legal_text" not in st.session_state:
        st.session_state.legal_text = ""
    if "summary" not in st.session_state:
        st.session_state.summary = ""
    if "followups" not in st.session_state:
        st.session_state.followups = []
    if "followup_input" not in st.session_state:
        st.session_state.followup_input = ""

    # File uploader
    uploaded_file = st.file_uploader("Upload file", type=["pdf", "doc", "docx", "txt"])

    # Process the uploaded file.
    if uploaded_file is not None and st.session_state.legal_text == "":
        legal_text = ""
        file_type = uploaded_file.name.split('.')[-1].lower()
        if file_type == "pdf":
            legal_text = read_pdf(uploaded_file)
        elif file_type in ["doc", "docx"]:
            legal_text = read_docx(uploaded_file)
        elif file_type == "txt":
            try:
                legal_text = uploaded_file.read().decode("utf-8")
            except Exception as e:
                st.error(f"Error reading TXT file: {e}")
        else:
            st.error("Unsupported file type.")

        if legal_text.strip() == "":
            st.error("No legal document content provided.")
        else:
            st.session_state.legal_text = legal_text
            st.info("Analyzing document...")
            st.session_state.summary = analyze_document(legal_text)

    # Display the analysis summary.
    if st.session_state.summary:
        st.subheader("Document Analysis Summary:")
        st.write(st.session_state.summary)

    # Display previous follow-up interactions.
    if st.session_state.followups:
        st.markdown("### Previous Follow-Up Interactions")
        for idx, qa in enumerate(st.session_state.followups, 1):
            st.markdown(f"**Follow-Up #{idx}:**")
            st.markdown(f"**Question:** {qa['question']}")
            st.markdown(f"**Answer:** {qa['answer']}")
            st.markdown("---")

    # Render the Follow-Up Questions section at the bottom (no extra line before header).
    if st.session_state.legal_text:
        st.subheader("Follow-Up Questions")
        st.write("Do you have any other questions? Is there anything else I can help you with?")
        if len(st.session_state.followups) < 20:
            st.text_input(
                "Enter your follow-up question here:",
                key="followup_input",
                on_change=submit_followup,
                value=""
            )
        else:
            st.warning("You have reached the maximum number of follow-up questions (20).")

if __name__ == '__main__':
    main()
