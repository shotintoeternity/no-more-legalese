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
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
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

def main():
    st.title("No More Legalese")
    st.write("Upload a PDF, DOC/DOCX, or TXT file for analysis.")

    # Initialize session state variables if not already present.
    if "legal_text" not in st.session_state:
        st.session_state.legal_text = ""
    if "summary" not in st.session_state:
        st.session_state.summary = ""
    if "followups" not in st.session_state:
        st.session_state.followups = []
    if "scroll_down" not in st.session_state:
        st.session_state.scroll_down = False

    uploaded_file = st.file_uploader("Upload file", type=["pdf", "doc", "docx", "txt"])

    # Automatically process and analyze the document once uploaded.
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
    
    # Always display the analysis summary if available.
    if st.session_state.summary:
        st.subheader("Document Analysis Summary:")
        st.write(st.session_state.summary)

    # Follow-up questions section (only available after a document has been analyzed)
    if st.session_state.legal_text:
        st.markdown("---")
        st.subheader("Follow-Up Questions")
        st.write("Do you have any other questions? Is there anything else I can help you with?")
        
        # Allow follow-up submissions up to 20 times.
        if len(st.session_state.followups) < 20:
            form_key = f"followup_form_{len(st.session_state.followups)}"
            with st.form(key=form_key, clear_on_submit=True):
                followup_question = st.text_input("Enter your follow-up question here:")
                submitted = st.form_submit_button("Submit Follow-Up")
                if submitted:
                    if followup_question.strip() == "":
                        st.error("Please enter a follow-up question.")
                    else:
                        st.info("Processing your follow-up question...")
                        answer = ask_followup(st.session_state.legal_text, followup_question)
                        st.session_state.followups.append({"question": followup_question, "answer": answer})
                        st.session_state.scroll_down = True  # Set flag to scroll down after submission.
        else:
            st.warning("You have reached the maximum number of follow-up questions (20).")

        # Display all previous follow-up interactions.
        if st.session_state.followups:
            st.markdown("### Previous Follow-Up Interactions")
            for idx, qa in enumerate(st.session_state.followups, 1):
                st.markdown(f"**Follow-Up #{idx}:**")
                st.markdown(f"**Question:** {qa['question']}")
                st.markdown(f"**Answer:** {qa['answer']}")
                st.markdown("---")

    # If a follow-up was just submitted, scroll to the bottom of the page.
    if st.session_state.get("scroll_down", False):
        st.markdown(
            """
            <script>
            window.scrollTo(0,document.body.scrollHeight);
            </script>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.scroll_down = False

if __name__ == '__main__':
    main()
