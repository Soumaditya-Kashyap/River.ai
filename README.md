# Multi-PDF Chatbot

AI-powered chatbot that summarizes multiple PDFs and answers questions about their content using Google Gemini AI.

## Features

- Upload multiple PDFs
- AI-generated summaries  
- Smart question suggestions
- Interactive chat with documents
- Horizontal card-based UI

## Setup

1. **Clone the repository**
```bash
git clone <https://github.com/Soumaditya-Kashyap/River.ai.git>
cd River
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Get Gemini API key**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create API key
   - Copy `.env.template` to `.env`
   - Add your key: `GEMINI_API_KEY=your_key_here`

4. **Run the app**
```bash
streamlit run app.py
```

5. **Open browser** → `http://localhost:8501`

## How to Use

### Single PDF
1. Upload PDF → Process → View summary → Chat

### Multiple PDFs  
1. Upload PDFs → Process → Select card (Combined/Individual) → Chat

## Tech Stack

Your Multi-PDF Chatbot uses **Streamlit** for the web interface, **Google Gemini AI** to understand and answer questions, **PyPDF2** to read PDF files, and **TF-IDF vectors** to find relevant content. When you ask a question, it converts your question to numbers, finds similar document chunks, and sends them to Gemini AI for smart answers.

## Requirements

- Python 3.8+
- Gemini API key (free)

## Files

- `app.py` - Main application
- `chat_interface.py` - Chat functionality  
- `model.py` - AI integration
- `pdf_processor.py` - PDF processing
- `summarizer.py` - Document summaries
- `check_env.py` - Environment check
- `demo.py` - API test

## Troubleshooting

**API Error**: Check your Gemini API key in `.env` file
**Import Error**: Run `pip install -r requirements.txt`
**PDF Error**: Ensure PDFs are not password-protected

## Environment Check

```bash
python check_env.py
```

This verifies Python version, dependencies, API key, and connectivity.

---

