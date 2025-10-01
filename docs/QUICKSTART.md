# Quick Start Guide

Get your Resume Optimization Agent up and running in 5 minutes!

## Step 1: Install Dependencies (2 min)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Key (1 min)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Anthropic API key
# Get your key at: https://console.anthropic.com
nano .env  # or use your preferred editor
```

Your `.env` should look like:
```env
ANTHROPIC_API_KEY=sk-ant-api03-xxx...
```

## Step 3: Run Setup Script (30 seconds)

```bash
python setup.py
```

This will:
- ✅ Verify Python version (3.10+)
- ✅ Check dependencies
- ✅ Validate API key
- ✅ Create necessary directories
- ✅ Initialize database

## Step 4: Launch the App (30 seconds)

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

## Step 5: Try It Out!

### First Interaction

1. **Upload a Resume** (sidebar)
   - Click "Browse files"
   - Select your resume (PDF, DOCX, or TXT)
   - Click "Parse Resume"

2. **Ask a Question**
   ```
   Analyze my resume and give me an overview of my strengths
   ```

3. **Compare to a Job**
   ```
   I'm applying for a Senior Python Developer role. Here's the description:
   [paste job description]

   How well does my resume match?
   ```

4. **Get Optimizations**
   ```
   Optimize my professional summary to better match this job
   ```

## Example Workflow

```
You: Upload resume.pdf

You: "Analyze my resume"

Agent: [Parses resume, provides overview of skills, experience]

You: "I want to apply for this Senior Software Engineer role at TechCorp:
[paste job description]"

Agent: [Analyzes job, compares to resume, provides match score and gaps]

You: "What should I improve first?"

Agent: [Provides prioritized recommendations]

You: "Optimize my work experience section for this job"

Agent: [Provides rewritten content with better keywords and positioning]
```

## Common Commands

```bash
# Start the app
streamlit run app.py

# Run setup verification
python setup.py

# Install/update dependencies
pip install -r requirements.txt --upgrade

# Initialize database
python -c "from models.database import init_db; init_db()"
```

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt --upgrade
```

### API key errors
- Check your `.env` file has `ANTHROPIC_API_KEY=sk-ant-...`
- Verify the key is valid at https://console.anthropic.com

### Database errors
```bash
python -c "from models.database import init_db; init_db()"
```

### App won't start
```bash
# Check if port 8501 is in use
lsof -i :8501  # Linux/Mac
netstat -ano | findstr :8501  # Windows

# Use different port
streamlit run app.py --server.port 8502
```

## Next Steps

1. **Explore Features**
   - Parse multiple resume versions
   - Analyze different job postings
   - Generate optimized bullet points
   - Check ATS compatibility

2. **Customize**
   - Edit `config.py` for model settings
   - Modify `agent/prompts.py` for custom prompts
   - Adjust `app.py` for UI changes

3. **Learn More**
   - Read the full [README.md](README.md)
   - Check tool documentation in `tools/`
   - Review agent architecture in `agent/`

## Support

- 📖 Full documentation: [README.md](README.md)
- 🐛 Issues: Create a GitHub issue
- 💡 Feature requests: Open a discussion

---

**You're all set! Start optimizing your resume with AI.**
