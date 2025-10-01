# Debug Summary: Agent Tool Calling Issue

## Problem
The agent was not calling the `parse_resume` tool even when users provided valid file paths. Instead, it responded conversationally without taking action.

## Root Cause
**Passive System Prompt** - The original system prompt was too conversational and didn't explicitly instruct the agent WHEN to use tools.

Original prompt said:
- "You have access to powerful tools..."
- "Typical workflow: 1. Parse the user's resume..."

This gave the agent permission to use tools but didn't **require** it to.

## Diagnosis Steps

### 1. ✅ Verified Tool Registration
- Checked `agent/orchestrator.py` - all 8 tools properly registered
- Tools list includes `parse_resume` at line 39

### 2. ✅ Tested Tool Directly
```bash
python -c "from tools.resume_parser import parse_resume; ..."
```
Result: **Tool works perfectly** - successfully parsed Franklin's resume from DOCX

### 3. ✅ Identified Issue
Agent was ignoring explicit file paths like:
```
"Please parse my resume at: /home/.../resume_20251001_053644.docx"
```

And responding with:
```
"I need you to upload your resume file..."
```

This is a **prompt engineering issue**, not a code bug.

## Solution Implemented

### Modified System Prompt (`agent/prompts.py`)

**Key Changes:**

1. **Added "CRITICAL" Directive**
```
CRITICAL: You MUST use your tools to analyze resumes and jobs.
DO NOT provide advice without first using the appropriate tool.
```

2. **Explicit Tool Usage Rules**
- Listed exactly WHEN to use each tool
- Used bold **ALWAYS** to emphasize requirements
- Added "DO NOT ASK if they want you to parse - JUST DO IT"

3. **Added Example Interactions**
```
User: "Please parse my resume at: /path/to/resume.pdf"
You: [Call parse_resume immediately with that path, then show results]
```

4. **Removed Ambiguity**
- Changed from "You have access to tools"
- To "WHEN USER PROVIDES A FILE PATH → Immediately call parse_resume"

### Updated App Reset Logic (`app.py`)

Added `st.session_state.agent = None` to force agent recreation when starting new conversation.

## Testing Instructions

### Test 1: Resume Upload
1. Click "🆕 New Conversation" in sidebar (forces prompt reload)
2. Upload a resume file
3. Say: "Please parse my resume at: [file path shown]"
4. **Expected**: Agent immediately calls parse_resume and shows structured data

### Test 2: Direct File Path
1. New conversation
2. Paste: "Parse /home/frankmark94/ResumeOptimizationAgent/data/resumes/resume_20251001_053644.docx"
3. **Expected**: Tool called automatically, no questions asked

### Test 3: Job Analysis
1. With parsed resume
2. Paste a job description
3. **Expected**: Agent calls analyze_job_description automatically

### Test 4: Gap Analysis
1. With both resume and job data
2. Ask: "How well does my resume match?"
3. **Expected**: Agent calls compare_resume_to_job

## Verification

Run this to see parsed resume data:
```bash
source venv/bin/activate
python -c "
from tools.resume_parser import parse_resume
result = parse_resume.invoke({
    'file_path': '/home/frankmark94/ResumeOptimizationAgent/data/resumes/resume_20251001_053644.docx'
})
print(result[:1000])
"
```

## Files Modified

1. **agent/prompts.py** - Completely rewrote SYSTEM_PROMPT to be more directive
2. **app.py** - Added agent reset on new conversation

## Next Steps for User

1. **Restart Streamlit** (Ctrl+C, then `streamlit run app.py`)
2. **Click "🆕 New Conversation"** to reload the agent with new prompts
3. **Try uploading resume again**
4. **Provide explicit prompts** like:
   - "Parse my resume at: [path]"
   - "Analyze this job: [paste description]"
   - "How well do I match this role?"

## Why This Happened

**LLMs are conversational by default.** Without explicit instructions to take action, Claude (even Sonnet 4) will default to:
- Explaining what it can do
- Asking clarifying questions
- Being helpful but passive

**Solution**: Make prompts **action-oriented** with:
- "ALWAYS do X when Y"
- "Immediately call tool Z"
- "DO NOT ask, just do it"

This is a common pattern in agentic systems - tools must be **prescribed**, not just **available**.

## Related Issues to Monitor

1. If agent still doesn't call tools → Check verbose=True logs in terminal
2. If tools fail → Check file permissions and paths
3. If Claude API errors → Check API key and rate limits

## Success Criteria

✅ Agent calls parse_resume when given file path
✅ Agent analyzes jobs when given job text
✅ Agent compares resume to jobs automatically
✅ No more "I need you to upload" when path is provided
✅ Data-driven recommendations instead of generic advice

---

**Status: FIXED - Awaiting User Testing**
