# Current Project Context - Resume Optimization Agent

**Last Updated:** 2025-10-01
**Project Status:** Phase 2 Complete + Manual Job Description Support Added

---

## Recent Work Summary

### What We Just Completed
**Fixed document generation to support manually pasted job descriptions** - Users can now generate resumes/cover letters for ANY job, not just those from Adzuna search results.

**Changes Made:**
1. Created `save_manual_job_description()` tool in `tools/job_search_tools.py`:
   - Takes job description text as input
   - Extracts job title and company name
   - Generates unique job_id from description hash
   - Calculates match score if resume available
   - Adds to session for document generation

2. Updated `agent/orchestrator.py`:
   - Imported and registered new tool (18 tools total now)
   - Added to Job Search Tools (Priority 3)

3. Updated `agent/prompts.py`:
   - Added explicit instructions for handling user-pasted job descriptions
   - Instructs agent to call `save_manual_job_description()` when user provides job text
   - Updated tool count from 16 to 18

**User Request That Triggered This:**
> "the agent said it couldn't generate a pDF because the job posting wasn't in their list... this isn't the intended behavior, I should be able to get a generarated PDF regardless of whether it has the job posting"

**How It Works Now:**
1. User pastes job description (e.g., Capital One Product Manager)
2. Agent calls `save_manual_job_description()` with the text
3. Tool creates JobPosting object with generated ID
4. Agent can now call `generate_optimized_resume()` with that ID
5. User gets downloadable PDF/DOCX

---

## Project Architecture Overview

### Core Components
- **LangChain Agent** (`agent/orchestrator.py`) - Tool-calling agent with Claude Sonnet 4
- **18 Specialized Tools** - Organized in 6 priority categories
- **Session Management** (`utils/session_state.py`) - Tracks context across conversation
- **Streamlit UI** (`app.py`) - Interactive web interface with chat
- **Job Search Service** (`services/job_search_service.py`) - Adzuna API integration
- **Document Service** (`services/document_service.py`) - PDF/DOCX generation with ReportLab

### 18 Agent Tools (Priority Order)

**1. Session Context (Priority 1)**
- `check_resume_status()` - Check if resume already uploaded
- `get_session_context()` - Get full conversation history

**2. Resume Tools (Priority 2)**
- `parse_resume()` - Extract structured data from PDF/DOCX

**3. Job Search Tools (Priority 3)**
- `search_jobs_by_criteria()` - Search Adzuna API
- `get_job_details()` - Get full job posting details
- `filter_jobs_by_requirements()` - Filter by match score, remote, salary
- `list_available_jobs()` - List jobs in current session
- `save_manual_job_description()` - **NEW** Save user-pasted job descriptions

**4. Job Analysis Tools (Priority 4)**
- `analyze_job_description()` - Extract requirements and skills
- `extract_job_keywords()` - Find ATS keywords
- `compare_resume_to_job()` - Gap analysis
- `calculate_match_score()` - Compatibility score (0-100%)

**5. Resume Optimization Tools (Priority 5)**
- `optimize_resume_section()` - Rewrite sections for job fit
- `generate_resume_bullets()` - Create achievement bullets
- `improve_ats_compatibility()` - Enhance keyword density

**6. Document Generation Tools (Priority 6)**
- `generate_optimized_resume()` - Create tailored PDF/DOCX resume
- `generate_cover_letter()` - Generate personalized cover letter PDF
- `list_generated_documents()` - Show all generated documents

---

## Key Features Implemented

### Phase 1 ✅ (Completed Earlier)
- Resume parsing (PDF/DOCX) with structured data extraction
- Job description analysis and keyword extraction
- Resume-to-job comparison with match scoring
- Section-by-section optimization suggestions
- ATS compatibility analysis
- Conversation memory and session management

### Phase 2 ✅ (Completed Recently)
- **Real-time job search** via Adzuna API (500 calls/month free tier)
- **Automatic job ranking** by match score (0-100%)
- **Interactive job cards** with salary, location, remote status
- **PDF/DOCX resume generation** with LLM-optimized summary
- **Personalized cover letter creation** with 3 tone options
- **In-line download buttons** in chat interface
- **Manual job description support** (just added!)

---

## Recent Bug Fixes

### Fix 1: Missing Dependencies
**Problem:** App crashed with `ModuleNotFoundError: No module named 'docxtpl'`
**Solution:** Installed missing packages: `pip install docxtpl langgraph langgraph-supervisor`
**Location:** `requirements.txt` updated

### Fix 2: Max Iterations Loop
**Problem:** Agent hit 10-iteration limit when user said "create a resume" without specifying job
**Root Cause:** `generate_optimized_resume()` requires job_id, agent had no mechanism to handle missing parameter
**Solutions Applied:**
1. Created `list_available_jobs()` tool - agent can check what jobs exist
2. Updated system prompt with 4-step workflow for missing job_id
3. Increased max_iterations from 10 to 15
4. Added `early_stopping_method="generate"` for graceful degradation
**Location:** `tools/job_search_tools.py:248`, `agent/orchestrator.py:152`, `agent/prompts.py:32`

### Fix 3: Manual Job Description Support (Just Completed)
**Problem:** Agent refused to generate PDF for user-pasted job descriptions, only accepted search results
**Root Cause:** Document generation required job to be in `session.current_job_search_results` from Adzuna
**Solution:** Created `save_manual_job_description()` tool to save any job description to session
**Location:** `tools/job_search_tools.py:248-354`, `agent/orchestrator.py:110`, `agent/prompts.py:20-24`

---

## Configuration & Setup

### Environment Variables Required
```bash
# Required API Keys
ANTHROPIC_API_KEY=your_key_here
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

# Model Settings
MODEL_NAME=claude-sonnet-4-20250514
TEMPERATURE=0.7
MAX_TOKENS=4096
```

### Installation
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install all dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

---

## Testing Checklist

### Manual Job Description Workflow (NEW - Needs Testing)
- [ ] User pastes job description → Agent calls `save_manual_job_description()`
- [ ] Tool extracts title and company correctly
- [ ] Job is added to `session.current_job_search_results`
- [ ] Match score calculated if resume available
- [ ] Agent can generate resume with returned job_id
- [ ] PDF/DOCX downloads successfully
- [ ] Job appears in `list_available_jobs()` output

### Core Workflows (Previously Tested)
- [x] Resume upload and parsing
- [x] Job search with Adzuna API
- [x] Job ranking by match score
- [x] Resume generation from search results
- [x] Cover letter generation
- [x] Document downloads
- [x] Session persistence across messages

---

## Known Issues & Limitations

### Current Limitations
1. **Job title/company extraction is basic** - Uses first line of pasted job description
2. **Location not extracted** - Defaults to "Location Not Specified" for manual jobs
3. **No salary extraction** - Manual jobs won't have salary info
4. **Remote type detection is simple** - Searches for "remote"/"hybrid" keywords only

### Future Improvements Needed
1. Use LLM to extract structured data from pasted job descriptions (title, company, location, salary, requirements)
2. Add support for job posting URLs (scrape and parse)
3. Allow editing of saved job details
4. Add "delete job" functionality from session
5. Persist jobs across sessions (database or file storage)

---

## File Structure

```
ResumeOptimizationAgent/
├── agent/
│   ├── orchestrator.py       # Agent setup with 18 tools
│   └── prompts.py            # System prompt and templates
├── tools/
│   ├── resume_parser.py      # Resume parsing tools
│   ├── job_analyzer.py       # Job analysis tools
│   ├── resume_comparator.py  # Comparison tools
│   ├── resume_optimizer.py   # Optimization tools
│   ├── session_tools.py      # Session management tools
│   ├── job_search_tools.py   # Job search + manual save (RECENTLY MODIFIED)
│   └── document_generation_tools.py  # PDF/DOCX generation
├── services/
│   ├── job_search_service.py # Adzuna API integration
│   └── document_service.py   # ReportLab/docxtpl document generation
├── utils/
│   ├── session_state.py      # Session state management
│   └── ui_components.py      # Streamlit reusable components
├── models/
│   └── schemas.py            # Pydantic data models (JobPosting, etc.)
├── config.py                 # Settings and environment variables
├── app.py                    # Streamlit UI (RECENTLY MODIFIED)
├── requirements.txt          # Python dependencies
└── docs/
    ├── CURRENT_CONTEXT.md    # This file
    ├── QUICKSTART.md         # Getting started guide
    └── [other docs]
```

---

## Next Steps / Roadmap

### Immediate Testing Needed
1. Test manual job description workflow end-to-end
2. Verify job title/company extraction works reasonably
3. Confirm match score calculation for manual jobs
4. Test PDF generation with manual jobs

### Phase 3 Planning (Future)
- LinkedIn profile optimization
- Interview preparation assistant
- Salary negotiation guidance
- Application tracking dashboard
- Multi-resume management (different versions for different roles)
- Email composition for outreach/networking

---

## Git Commits (Recent)

```
a02a218 - Add job search and document generation capabilities
82548a8 - Update README with Phase 2 features
89fa750 - Fix max iterations issue with document generation
[pending] - Add support for manually pasted job descriptions
```

---

## Quick Reference Commands

```bash
# Start app
streamlit run app.py

# Install new dependencies
pip install -r requirements.txt

# Check logs
# (Set verbose=True in orchestrator.py line 151 for detailed agent logs)

# Reset session
# Click "Clear Session" button in sidebar

# Check API usage
# Adzuna: 500 calls/month free tier
# Anthropic: Check dashboard at console.anthropic.com
```

---

## Notes for Next Session

1. **Test the manual job description feature** - This was just implemented and needs validation
2. **Consider improving extraction** - Current job title/company extraction is very basic (just uses first line)
3. **Check agent behavior** - Verify agent calls `save_manual_job_description()` when user pastes job text
4. **Monitor max iterations** - Watch for any new iteration issues with the added tool
5. **User experience** - Get feedback on whether workflow feels natural

---

## Contact & Resources

- **Adzuna API Docs:** https://developer.adzuna.com/docs
- **LangChain Tool Calling:** https://python.langchain.com/docs/modules/agents/
- **Claude API:** https://docs.anthropic.com/claude/reference/
- **ReportLab PDF:** https://docs.reportlab.com/
- **Streamlit:** https://docs.streamlit.io/

---

**Remember:** This is a working document. Update it whenever you make significant changes or fix important bugs. It's designed to help you (and future you) quickly understand where the project stands and what was recently worked on.
