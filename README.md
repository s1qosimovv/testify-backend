# QuizGen AI Backend

FastAPI backend for AI-powered quiz generation from documents.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=1500
HOST=0.0.0.0
PORT=8000
```

### 3. Run the Server

```bash
# From the backend directory
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
python app/main.py
```

### 4. Test the API

Open http://localhost:8000/docs to see the interactive API documentation.

## 📡 API Endpoints

### POST /api/upload-file
Upload a file (PDF, DOCX, or TXT) and extract text.

**Request:** multipart/form-data with `file`

**Response:**
```json
{
  "text": "extracted text content..."
}
```

### POST /api/generate-quiz
Generate quiz from text using AI.

**Request:**
```json
{
  "text": "your text content..."
}
```

**Response:**
```json
{
  "quiz_id": "uuid-here",
  "quiz": {
    "quiz": [
      {
        "question": "Sample question?",
        "options": {
          "A": "Option A",
          "B": "Option B",
          "C": "Option C",
          "D": "Option D"
        },
        "correct_answer": "B"
      }
    ]
  }
}
```

### POST /api/submit-answers?quiz_id={id}
Submit answers for evaluation.

**Request:**
```json
{
  "answers": {
    "0": "A",
    "1": "C",
    "2": "B"
  }
}
```

**Response:**
```json
{
  "score": 8,
  "total": 10,
  "percentage": 80.0
}
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── api/
│   │   └── routes.py        # API endpoints
│   ├── services/
│   │   ├── file_reader.py   # File processing
│   │   ├── ai_service.py    # OpenAI integration
│   │   └── quiz_service.py  # Quiz logic
│   └── models/
│       └── quiz.py          # Pydantic models
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Development

- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 📦 Dependencies

- **FastAPI**: Modern web framework
- **OpenAI**: AI quiz generation
- **PyMuPDF**: PDF text extraction
- **python-docx**: DOCX text extraction
- **Pydantic**: Data validation
