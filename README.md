# Interview Preparation Chatbot

An AI-powered interview preparation platform that helps users practice for technical and behavioral interviews, get resume feedback, and improve their interview skills.

## Features

- **Resume Analysis**: Upload your resume and get detailed feedback on content, formatting, and ATS compatibility.
- **Interview Simulation**: Practice with realistic interview questions based on your target role and experience level.
- **Personalized Feedback**: Receive AI-powered feedback on your responses, including areas for improvement and sample answers.
- **Question Bank**: Access a growing library of interview questions across various domains and difficulty levels.
- **Progress Tracking**: Monitor your improvement over time with detailed analytics and performance metrics.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React.js (to be implemented)
- **AI/ML**: OpenAI GPT-4 for response analysis and feedback
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT-based authentication
- **File Storage**: Local filesystem (development), S3 (production)

## Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend)
- OpenAI API key
- (Optional) PostgreSQL for production

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/interview-chatbot.git
   cd interview-chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-openai-api-key
   DATABASE_URL=sqlite:///./interview_chatbot.db
   ```

6. Run database migrations (when implemented):
   ```bash
   alembic upgrade head
   ```

7. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

8. (Optional) Start the frontend development server:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
interview-chatbot/
├── app/                          # Backend application
│   ├── core/                     # Core functionality
│   ├── models/                   # Database models
│   ├── routers/                  # API route handlers
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── interview.py          # Interview simulation endpoints
│   │   └── resume.py             # Resume analysis endpoints
│   ├── schemas/                  # Pydantic models
│   ├── services/                 # Business logic
│   │   ├── interview_simulator.py # Interview simulation logic
│   │   └── resume_parser.py      # Resume parsing logic
│   └── main.py                  # FastAPI application
├── tests/                       # Test files
├── static/                      # Static files
├── data/                        # Data storage (resumes, etc.)
└── requirements.txt             # Python dependencies
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Secret key for JWT token generation | - |
| `OPENAI_API_KEY` | API key for OpenAI services | - |
| `DATABASE_URL` | Database connection URL | `sqlite:///./interview_chatbot.db` |
| `UPLOAD_DIR` | Directory for uploaded files | `./data/uploads` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG` | Enable debug mode | `False` |

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



