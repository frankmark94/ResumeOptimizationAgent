# Resume Optimization Agent 📄

An AI-powered career advisor that helps job seekers optimize their resumes and find relevant job opportunities through intelligent analysis and personalized recommendations using Claude Sonnet 4 and LangChain.

## Features

### Core Capabilities
- **Resume Parsing**: Extract structured data from PDF, DOCX, and TXT resume files
- **Job Analysis**: Analyze job descriptions to extract requirements and keywords
- **Gap Analysis**: Compare resumes against jobs to identify skill gaps and matches
- **Resume Optimization**: AI-powered content optimization for specific job postings
- **ATS Scoring**: Evaluate and improve Applicant Tracking System compatibility
- **Bullet Generation**: Create achievement-focused bullet points

### Technical Stack
- **LangChain**: Agent orchestration and tool management
- **Claude Sonnet 4**: Advanced AI analysis and content generation
- **Streamlit**: Interactive web interface
- **SQLAlchemy**: Database management
- **Pydantic**: Data validation

## Project Structure

```
job_agent/
├── app.py                      # Streamlit UI
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
│
├── agent/
│   ├── orchestrator.py        # LangChain agent setup
│   └── prompts.py             # System prompts
│
├── tools/
│   ├── resume_parser.py       # Resume parsing
│   ├── job_analyzer.py        # Job description analysis
│   ├── resume_comparator.py   # Resume-job comparison
│   └── resume_optimizer.py    # Content optimization
│
├── models/
│   ├── schemas.py             # Pydantic data models
│   └── database.py            # SQLAlchemy models
│
└── data/
    ├── resumes/               # Uploaded resumes
    ├── generated/             # Generated content
    └── applications.db        # SQLite database
```

## Installation

### Prerequisites
- Python 3.10 or higher
- Anthropic API key (for Claude)

### Setup Steps

1. **Clone the repository**
```bash
cd ResumeOptimizationAgent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

5. **Initialize database**
```bash
python -c "from models.database import init_db; init_db()"
```

## Usage

### Start the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Quick Start Guide

1. **Upload Your Resume**
   - Use the sidebar to upload your resume (PDF, DOCX, or TXT)
   - Click "Parse Resume" to extract structured data

2. **Analyze a Job**
   - Paste a job description in the chat
   - Example: "I'm applying for [Job Title] at [Company]. Here's the description: [paste text]"

3. **Get Optimization Suggestions**
   - The agent will analyze the match and provide recommendations
   - Ask for specific optimizations: "Optimize my summary section"

4. **Generate Content**
   - Request bullet points: "Generate 5 bullet points for my Software Engineer role"
   - Ask for rewrites: "Rewrite this section to match the job requirements"

### Example Prompts

```
"Analyze my resume and give me an overview"

"I want to apply for this job: [paste job description]. How well does my resume match?"

"What are the top 5 skills I'm missing for this role?"

"Optimize my work experience section for this job"

"Generate achievement-focused bullets for my current role"

"Check my resume's ATS compatibility for these keywords: Python, AWS, Docker"
```

## Agent Tools

The agent has access to 8 specialized tools:

1. **parse_resume**: Extract structured data from resume files
2. **analyze_job_description**: Extract requirements from job postings
3. **extract_job_keywords**: Identify technical keywords
4. **compare_resume_to_job**: Perform gap analysis
5. **calculate_match_score**: Quick skill matching
6. **optimize_resume_section**: Rewrite content for jobs
7. **generate_resume_bullets**: Create new bullet points
8. **improve_ats_compatibility**: Enhance ATS scoring

## Configuration

Edit `config.py` to customize:

- **Model**: Claude model to use (default: claude-sonnet-4-20250514)
- **Temperature**: Response creativity (0.0-1.0)
- **Max Tokens**: Response length limit
- **Database Path**: SQLite database location

## API Keys

### Required
- **Anthropic API Key**: Get it at [console.anthropic.com](https://console.anthropic.com)

### Optional (for job search features)
- Indeed API Key
- LinkedIn API Key
- Adzuna API credentials

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## Roadmap

### Phase 1: MVP (Current)
- ✅ Resume parsing and analysis
- ✅ Job description analysis
- ✅ Gap analysis and comparison
- ✅ Content optimization
- ✅ Basic Streamlit UI

### Phase 2: Job Search
- 🔲 Automated job search from APIs
- 🔲 Job ranking by relevance
- 🔲 Application tracking system
- 🔲 Resume version management

### Phase 3: Advanced Features
- 🔲 Cover letter generation
- 🔲 Semantic job matching with vector DB
- 🔲 Export to PDF/DOCX
- 🔲 Interview preparation suggestions

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt --upgrade
```

**API Key Errors**
```bash
# Verify your .env file has the correct API key
cat .env | grep ANTHROPIC_API_KEY
```

**Database Errors**
```bash
# Reinitialize the database
python -c "from models.database import init_db; init_db()"
```

**File Upload Issues**
- Ensure `data/resumes` directory exists
- Check file permissions
- Verify file format (PDF, DOCX, TXT only)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation

## Acknowledgments

- Built with [LangChain](https://langchain.com)
- Powered by [Anthropic Claude](https://anthropic.com)
- UI with [Streamlit](https://streamlit.io)

---

**Note**: This is an MVP version focused on core resume optimization features. Job search and application tracking features will be added in future releases.
