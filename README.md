# No More Legalese

No More Legalese is a Streamlit application that allows users to upload legal documents (PDF, DOC, DOCX, TXT) for automatic analysis. The application summarizes the legal document, explains its overall structure and key components, and provides a follow-up interface for users to ask additional questions. The backend is powered by the Groq API.

## Features

- **File Upload:** Supports PDF, DOC, DOCX, and TXT formats.
- **Automatic Analysis:** Automatically processes and analyzes the uploaded document.
- **Summary Display:** Provides a detailed summary of the legal document’s structure and content.
- **Follow-Up Questions:** Users can ask up to 20 follow-up questions, with a dynamic form that always appears at the bottom.
- **Persistent Content:** All previous analysis and follow-up interactions remain visible on the page.
- **Environment Variables:** Loads the Groq API key from a `.env` file.

## Installation

1. **Clone the Repository:**
    ```
    git clone https://github.com/yourusername/no-more-legalese.git
    cd no-more-legalese
    ```

2. **Create and Activate a Virtual Environment (Optional but Recommended):**
    ```
    python -m venv venv
    source venv/bin/activate   # On Windows use: venv\Scripts\activate
    ```

3. **Install Dependencies:**
    ```
    pip install -r requirements.txt
    ```

4. **Setup Environment Variables:**
    - Create a file named `.env` in the project root with the following content:
      ```
      GROQ_API_KEY=your_actual_api_key
      ```

## Usage

Run the application using Streamlit:

	```
	streamlit run app.py
	```

- Upload your legal document (PDF, DOC, DOCX, or TXT) to automatically start the analysis.
- Review the document analysis summary.
- Ask follow-up questions in the provided interface; each new question appears at the bottom of the page.

## Dependencies

The project requires the following libraries:
- streamlit
- groq
- python-dotenv
- PyPDF2
- python-docx

These are listed in the `requirements.txt` file.

## License

This project is licensed under the MIT License.
