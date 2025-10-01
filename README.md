# Resume Optimization Agent 📄

<div align="center">
  <img src="readmepics/MainLogo.png" alt="Resume Optimization Agent" width="800"/>

  **AI-powered career advisor to optimize your resume and find relevant jobs**

  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![LangChain](https://img.shields.io/badge/langchain-0.1.0+-purple.svg)](https://langchain.com)
  [![Claude Sonnet 4](https://img.shields.io/badge/claude-sonnet--4-orange.svg)](https://anthropic.com)
  [![Streamlit](https://img.shields.io/badge/streamlit-1.30.0+-red.svg)](https://streamlit.io)
  [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
</div>

---

## 🎯 Overview

An AI-powered career advisor that helps job seekers optimize their resumes and find relevant job opportunities through intelligent analysis and personalized recommendations using Claude Sonnet 4 and LangChain.

**Key Features:**
- 🔍 **Resume Parsing** - Extract structured data from PDF, DOCX, and TXT files
- 🎯 **Job Search** - Find relevant jobs via Adzuna API with match scoring
- 📊 **Gap Analysis** - Compare resumes against jobs to identify skill gaps
- ✨ **AI Optimization** - Claude Sonnet 4-powered content improvements
- 📝 **Document Generation** - Create tailored resumes and cover letters as PDF/DOCX
- 💾 **Instant Downloads** - Download generated documents directly in chat
- 💬 **Context Memory** - Maintains conversation state across multiple interactions
- 🔧 **16 Specialized Tools** - Purpose-built agent tools for job search and optimization

---

## 🏗️ System Architecture

<div align="center">
  <img src="readmepics/Architecture Diagram.png" alt="System Architecture" width="700"/>
</div>

### Architecture Components

The system is built on a **modular, tool-based architecture** with four main layers:

#### 1. **UI Layer (Streamlit Interface)**
- File upload and resume management
- Interactive chat interface
- Real-time session state debugging
- Context-aware user experience

#### 2. **Agent Layer (LangChain + Claude Sonnet 4)**
- **LangChain Agent Orchestrator**: Coordinates tool selection and execution
- **Claude Sonnet 4 API**: Powers intelligent analysis and content generation
- **Memory Storage (SQLite)**: Persists conversation history and context
- **Conversation History**: Maintains multi-turn dialogue context

#### 3. **Tool Layer (16 Specialized Tools)**
- **Resume Parser**: Extracts structured data from documents
- **Job Search Tools**: Search, filter, and rank job postings (Adzuna API)
- **Job Analyzer**: Analyzes job descriptions and requirements
- **Gap Analyzer**: Compares resumes to job requirements
- **Resume Optimizer**: Rewrites content for better job matches
- **Document Generator**: Creates optimized resumes and cover letters (PDF/DOCX)
- **Application Tracker**: Manages job application history

#### 4. **Data Layer**
- **SQLite DB**: Stores applications, resumes, and job data
- **File Storage**: Manages uploaded PDF/DOCX files
- **Vector Store**: Optional ChromaDB for semantic search

---

## 🔄 Data Flow

<div align="center">
  <img src="readmepics/Data Flow.png" alt="Data Flow Diagram" width="700"/>
</div>

### Process Flow Explanation

#### User Layer (TO-DO)
1. **Upload Resume PDF** → Sends file to Agent System
2. **Provides Job Preferences** → Communicates requirements to Agent
3. **Reviews Optimized Resume** → Receives enhanced version (TO-45)

#### Agent System
1. **Parses Resume** → Extracts structured data from PDF
2. **Searches Jobs** → Queries Adzuna API for matching positions
3. **Ranks Results** → Calculates match scores based on resume skills
4. **Generates Documents** → Creates optimized resumes and cover letters
5. **Optimizes Content** → Uses Claude API to tailor content to jobs

#### External Services
- **Claude API (LLM Processing)** → Analyzes and generates content
- **Adzuna API (Job Search)** → Real-time job search and filtering
- **File Storage (PDF/DOCX files)** → Stores original and generated documents
- **Database (Application Tracking)** → Persists job applications and matches

This **asynchronous workflow** ensures the agent can handle multiple requests efficiently while maintaining context across conversations.

---

## 🚀 Features

### Core Capabilities

#### Resume Management
- ✅ **Multi-format parsing**: PDF, DOCX, TXT support
- ✅ **Structured extraction**: Contact info, skills, experience, education
- ✅ **Version tracking**: Manage multiple resume variants
- ✅ **Session caching**: Instant access to parsed data

#### Job Search & Discovery 🆕
- ✅ **Real-time search**: Query Adzuna API for live job postings
- ✅ **Smart filtering**: Location, remote type, salary range filters
- ✅ **Match scoring**: Automatic ranking by resume compatibility (0-100%)
- ✅ **Interactive cards**: Rich job cards with salary, location, remote status
- ✅ **Job details**: Full descriptions, requirements, company info

#### Job Analysis
- ✅ **Requirement extraction**: Automatically identifies must-have skills
- ✅ **Keyword identification**: Detects ATS-critical terms
- ✅ **Experience level detection**: Matches seniority requirements
- ✅ **Company insights**: Analyzes job descriptions for cultural fit

#### Intelligent Comparison
- ✅ **Gap analysis**: Identifies missing skills and qualifications
- ✅ **Match scoring**: 0-100% compatibility rating
- ✅ **Partial matching**: Recognizes transferable skills
- ✅ **Priority ranking**: Highlights most important gaps

#### Content Optimization
- ✅ **Section rewriting**: Optimizes summaries, bullets, skills
- ✅ **Keyword incorporation**: Naturally integrates ATS keywords
- ✅ **Achievement focus**: Emphasizes quantifiable results
- ✅ **ATS compatibility**: Ensures parsing-friendly formatting

#### Document Generation 🆕
- ✅ **Resume generation**: Create optimized PDF/DOCX resumes for specific jobs
- ✅ **Cover letters**: AI-generated personalized cover letters
- ✅ **LLM optimization**: Professional summary rewritten for target role
- ✅ **ATS-friendly formatting**: ReportLab-powered professional layouts
- ✅ **Instant downloads**: Download buttons directly in chat interface

#### Context Memory System
- ✅ **Resume persistence**: Remembers uploaded files across conversation
- ✅ **Parsed data caching**: Instant retrieval without re-parsing
- ✅ **Session state tracking**: Maintains job search and document context
- ✅ **Smart tool selection**: Automatically uses cached data when available

---

## 🛠️ Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Claude Sonnet 4 | AI analysis and generation |
| **Agent Framework** | LangChain + LangGraph | Tool orchestration |
| **UI** | Streamlit | Interactive web interface |
| **Database** | SQLite + SQLAlchemy | Data persistence |
| **Validation** | Pydantic | Data modeling |
| **Document Parsing** | PyPDF2, python-docx | Resume extraction |
| **Document Generation** | ReportLab, docxtpl | PDF/DOCX creation |
| **Job Search** | Adzuna API | Real-time job discovery |
| **Session Management** | Custom SessionState | Context tracking |

---

## 📦 Project Structure

```
ResumeOptimizationAgent/
├── 📱 app.py                        # Streamlit UI with session integration
├── ⚙️ config.py                     # Configuration management
├── 📋 requirements.txt              # Python dependencies
├── 🔐 .env.example                  # Environment template
│
├── 🤖 agent/
│   ├── orchestrator.py              # LangChain agent + output parsing
│   └── prompts.py                   # Context-aware system prompts
│
├── 🔧 tools/
│   ├── resume_parser.py             # Resume parsing with caching
│   ├── job_search_tools.py          # 🆕 Job search and filtering
│   ├── document_generation_tools.py # 🆕 Resume & cover letter creation
│   ├── job_analyzer.py              # Job description analysis
│   ├── resume_comparator.py         # Gap analysis
│   ├── resume_optimizer.py          # Content optimization
│   └── session_tools.py             # Context awareness tools
│
├── 🏢 services/                     # 🆕 External integrations
│   ├── job_search_service.py        # Adzuna API wrapper
│   └── document_service.py          # PDF/DOCX generation
│
├── 📊 models/
│   ├── schemas.py                   # Pydantic data models
│   └── database.py                  # SQLAlchemy ORM
│
├── 🧰 utils/
│   ├── helpers.py                   # Utility functions
│   ├── session_state.py             # Session state manager
│   └── ui_components.py             # 🆕 Job cards & download buttons
│
├── 💾 data/
│   ├── resumes/                     # Uploaded files
│   ├── generated/                   # Optimized content
│   └── applications.db              # SQLite database
│
└── 📚 Documentation/
    ├── README.md                    # This file
    ├── QUICKSTART.md                # 5-minute setup guide
    ├── CONTEXT_MEMORY_FIX.md        # Context memory implementation
    └── DEBUGGING_REPORT.md          # Tool calling fixes
```

---

## 🎬 Installation

### Prerequisites
- Python 3.10 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com))
- Adzuna API credentials ([Sign up here](https://developer.adzuna.com)) - **Free tier: 500 calls/month**

### Quick Setup (5 Minutes)

```bash
# 1. Clone the repository
git clone https://github.com/frankmark94/ResumeOptimizationAgent.git
cd ResumeOptimizationAgent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
nano .env  # Add your API keys

# Required:
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# For job search (recommended):
ADZUNA_API_ID=your_app_id
ADZUNA_API_KEY=your_api_key

# 5. Initialize database
python -c "from models.database import init_db; init_db()"

# 6. Launch!
streamlit run app.py
```

The app will automatically open at `http://localhost:8501` 🎉

### Getting Adzuna API Credentials

1. Go to https://developer.adzuna.com/
2. Click "Sign Up" and create an account
3. Once logged in, find your App ID and API Key in the dashboard
4. Copy both values to your `.env` file

---

## 💡 Usage Guide

### Quick Start

1. **Upload Your Resume**
   - Use sidebar file uploader
   - Supports PDF, DOCX, TXT
   - Click "Parse Resume Now"

2. **Search for Jobs** 🆕
   ```
   "Find me Python developer jobs in San Francisco"
   "Search for remote senior engineer positions"
   "Show me data science jobs with salaries over $120k"
   ```

3. **Generate Documents** 🆕
   ```
   "Generate an optimized resume for the first job"
   "Create a cover letter for the Google position"
   "Generate a resume and cover letter for job ID 12345"
   ```

4. **Analyze & Optimize**
   ```
   "Analyze my match for the second job"
   "What skills am I missing for this role?"
   "Optimize my professional summary for this position"
   ```

### Example Conversation Flow

```
You: [Upload resume.pdf]
Agent: ✅ Resume uploaded and parsed!

You: "Find me senior Python engineer jobs in remote"
Agent: "I found 8 jobs matching your criteria. Here are the top 5..."
       [Displays interactive job cards with match scores]

You: [Click "Generate Resume" on Google job card]
Agent: "I've created an optimized resume for the Google Senior Python Engineer position.
        ✅ Emphasized your distributed systems experience
        ✅ Added keywords: Kubernetes, gRPC, Python 3.11
        ✅ Quantified impact in bullet points"
       [Download button appears]

You: "Generate a cover letter for this job too"
Agent: "Cover letter created! Highlighted your 5 years of cloud architecture experience..."
       [Download button appears]

You: [Download both documents]
```

---

## 🧰 Agent Tools (16 Total)

### Session Context Tools
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `check_resume_status` | Check if resume uploaded | None | Resume status, file path |
| `get_session_context` | Get conversation state | None | Session context summary |

### Job Search Tools 🆕
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `search_jobs_by_criteria` | Search for jobs | Query, location, remote type | Ranked job list |
| `get_job_details` | Get full job info | Job ID | Complete job posting |
| `filter_jobs_by_requirements` | Filter job results | Min score, filters | Filtered job list |

### Resume & Job Analysis Tools
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `parse_resume` | Extract resume data | File path | Structured JSON |
| `analyze_job_description` | Analyze job posting | Job text | Requirements, keywords |
| `extract_job_keywords` | Get technical terms | Job text | Keyword list |
| `compare_resume_to_job` | Gap analysis | Resume + Job | Match score, gaps |
| `calculate_match_score` | Quick scoring | Skills lists | Percentage match |

### Resume Optimization Tools
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `optimize_resume_section` | Rewrite content | Section + requirements | Optimized text |
| `generate_resume_bullets` | Create bullets | Role + skills | Bullet point list |
| `improve_ats_compatibility` | ATS analysis | Resume text | ATS score, tips |

### Document Generation Tools 🆕
| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `generate_optimized_resume` | Create tailored resume | Job ID, format | PDF/DOCX file path |
| `generate_cover_letter` | Create cover letter | Job ID, tone | PDF file path |
| `list_generated_documents` | Show generated docs | None | Document list |

### Tool Calling Example

```python
# Complete workflow - Job search to document generation:
1. check_resume_status()                      # See if resume already uploaded
2. parse_resume()                             # Extract data (uses cached if available)
3. search_jobs_by_criteria("Python", "SF")    # Find matching jobs
4. get_job_details(job_id="12345")            # Get full job info
5. compare_resume_to_job(resume, job)         # Calculate match score
6. generate_optimized_resume(job_id="12345")  # Create tailored PDF
7. generate_cover_letter(job_id="12345")      # Create personalized letter
```

---

## 🆕 Context Memory System

### Problem Solved
Previously, the agent would ask for the resume file path repeatedly, even after upload. This created a frustrating user experience.

### Solution
Implemented a **comprehensive session state management system** that:

- ✅ Tracks uploaded resume files across conversation turns
- ✅ Caches parsed resume data to avoid re-parsing
- ✅ Maintains conversation context and user profile
- ✅ Provides tools for the agent to check session state
- ✅ Automatically uses cached data when available

### How It Works

```python
# User uploads resume
session.set_resume(file_path, parsed_data)

# User asks: "What are my skills?"
agent.check_resume_status()  # Sees has_resume=true
agent.parse_resume()  # Uses cached data (instant!)
# Response uses cached data without asking for file again ✅
```

### Debug Panel

Open **"🔍 Session Debug Info"** in the sidebar to see:
- Resume uploaded: ✅/❌
- File path: `/path/to/resume.pdf`
- Parsed: ✅/❌
- Job provided: ✅/❌
- Recent activity log

See [`CONTEXT_MEMORY_FIX.md`](docs/CONTEXT_MEMORY_FIX.md) for complete implementation details.

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# LLM Settings
model_name = "claude-sonnet-4-20250514"  # Claude model
temperature = 0.7                         # Response creativity (0.0-1.0)
max_tokens = 4096                         # Response length

# Database
database_url = "sqlite:///./data/applications.db"

# File Paths
resume_dir = "data/resumes"
generated_dir = "data/generated"
```

---

## 🔑 API Keys

### Required
- **Anthropic API Key**: [Get it here](https://console.anthropic.com)
  ```env
  ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
  ```

### Recommended (For Job Search)
- **Adzuna API**: [Get it here](https://developer.adzuna.com) - Free tier: 500 calls/month
  ```env
  ADZUNA_API_ID=your_app_id
  ADZUNA_API_KEY=your_api_key
  ```

### Future Enhancements
- Indeed API Key (deprecated, will use web scraping)
- LinkedIn API Key (restricted access)

---

## 🧪 Testing

### Run Test Scripts

```bash
# Test agent tool calling
python test_agent_tool_calling.py

# Test response parsing
python test_response_parsing.py

# Debug prompt structure
python debug_prompt_structure.py
```

### Manual Testing Checklist

#### Core Features
- [ ] Upload resume → verify stored in session debug panel
- [ ] Parse resume → ask "what stands out?" → should NOT ask for file again
- [ ] Parse resume twice → second time uses cached data (instant)
- [ ] Click "New Conversation" → session resets correctly
- [ ] Multi-turn conversation maintains context

#### Job Search 🆕
- [ ] Search for jobs → "Find Python jobs in NYC"
- [ ] Job cards render with match scores
- [ ] Click "Generate Resume" on job card
- [ ] Click "Generate Cover Letter" on job card
- [ ] Download buttons work for both documents
- [ ] PDFs open correctly with proper formatting

---

## 🚧 Roadmap

### ✅ Phase 1: MVP (Complete)
- Resume parsing and analysis
- Job description analysis
- Gap analysis and comparison
- Content optimization
- Streamlit UI
- Context memory system
- Tool calling fixes

### ✅ Phase 2: Job Search & Documents (Complete)
- ✅ Real-time job search via Adzuna API
- ✅ Match score calculation and ranking
- ✅ Interactive job cards with filters
- ✅ Resume generation (PDF/DOCX)
- ✅ Cover letter generation (PDF)
- ✅ In-line download buttons
- ✅ Session state for jobs and documents
- ✅ 16 specialized agent tools

### 🔄 Phase 3: Multi-Agent Architecture (Planned)
- LangGraph Supervisor pattern
- Specialized sub-agents per domain (search, analysis, generation)
- Parallel tool execution
- Advanced error handling and retries

### 📅 Phase 4: Advanced Features (Future)
- Multi-source job aggregation (Indeed scraping, LinkedIn)
- Semantic job matching with ChromaDB vector store
- Application tracking dashboard
- Interview preparation suggestions
- Email drafting for outreach
- Chrome extension for job saves
- Resume A/B testing and analytics

---

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
pip install -r requirements.txt --upgrade
```

**API Key Errors**
```bash
# Verify .env file
cat .env | grep ANTHROPIC_API_KEY
```

**Database Errors**
```bash
python -c "from models.database import init_db; init_db()"
```

**Agent Not Using Tools**
- Check system prompt in `agent/prompts.py`
- Verify tools registered in `agent/orchestrator.py`
- See [`DEBUGGING_REPORT.md`](docs/DEBUGGING_REPORT.md) for tool calling fixes

**Session State Not Persisting**
- Check debug panel shows resume uploaded
- Verify `session.set_resume()` called on upload
- See [`CONTEXT_MEMORY_FIX.md`](docs/CONTEXT_MEMORY_FIX.md) for details

---

## 📚 Documentation

- **[QUICKSTART.md](docs/QUICKSTART.md)** - 5-minute setup guide
- **[CONTEXT_MEMORY_FIX.md](docs/CONTEXT_MEMORY_FIX.md)** - Context memory implementation
- **[DEBUGGING_REPORT.md](docs/DEBUGGING_REPORT.md)** - Tool calling & rendering fixes
- **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Complete implementation overview

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com) - Agent orchestration framework
- Powered by [Anthropic Claude](https://anthropic.com) - Sonnet 4 LLM
- UI with [Streamlit](https://streamlit.io) - Interactive web apps
- Inspired by the need for better job search tools

---

## 📞 Support

- 🐛 [Report Issues](https://github.com/frankmark94/ResumeOptimizationAgent/issues)
- 💬 [Discussions](https://github.com/frankmark94/ResumeOptimizationAgent/discussions)
- 📧 Contact: [GitHub Profile](https://github.com/frankmark94)

---

<div align="center">
  <strong>Built with ❤️ using LangChain, Claude Sonnet 4, and Streamlit</strong>

  ⭐ Star this repo if you find it helpful!
</div>
