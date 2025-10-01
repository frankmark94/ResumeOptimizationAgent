# Git & GitHub Setup Guide

## Current Status
✅ Git repository initialized
✅ .gitignore configured
✅ Branch renamed to 'main'

## Quick Start - Push to GitHub

### Option 1: Using GitHub CLI (Recommended)

```bash
# Install GitHub CLI if not already installed
# On Ubuntu/Debian:
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Login to GitHub
gh auth login

# Create repository and push
gh repo create ResumeOptimizationAgent --public --source=. --remote=origin --push
```

### Option 2: Manual GitHub Setup

1. **Create GitHub Repository**
   - Go to https://github.com/new
   - Name: `ResumeOptimizationAgent`
   - Description: "AI-powered resume optimization agent using Claude Sonnet 4 and LangChain"
   - Make it Public or Private
   - DON'T initialize with README (we already have one)
   - Click "Create repository"

2. **Configure Git User** (if not already done)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

3. **Add All Files**
```bash
git add .
```

4. **Create Initial Commit**
```bash
git commit -m "Initial commit: Resume Optimization Agent MVP

- Implemented LangChain agent with 8 specialized tools
- Resume parsing (PDF, DOCX, TXT)
- Job analysis and gap detection
- AI-powered content optimization
- Streamlit web interface
- SQLAlchemy database models
- Comprehensive documentation

Phase 1 (MVP) complete and ready for testing."
```

5. **Add Remote Repository**
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/ResumeOptimizationAgent.git
```

6. **Push to GitHub**
```bash
git push -u origin main
```

## Ongoing Git Workflow

### Make Changes and Commit

```bash
# Check status
git status

# Add specific files
git add app.py config.py

# Or add all changes
git add .

# Commit with message
git commit -m "Add feature: Cover letter generation"

# Push to GitHub
git push
```

### Create Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/job-search-api

# Make your changes
# ... edit files ...

# Commit changes
git add .
git commit -m "Implement Indeed API integration"

# Push branch to GitHub
git push -u origin feature/job-search-api

# Create pull request on GitHub
gh pr create --title "Add Indeed API integration" --body "Implements automated job search"
```

### Update from Remote

```bash
# Pull latest changes
git pull origin main

# Merge feature branch back to main
git checkout main
git merge feature/job-search-api
git push
```

## Important Files in Git

### Tracked Files
- All `.py` source files
- Configuration files (`.env.example`, `config.py`)
- Documentation (`.md` files)
- `requirements.txt`
- `.gitignore`

### Ignored Files (from .gitignore)
- `.env` (contains secrets)
- `__pycache__/` (Python cache)
- `venv/` (virtual environment)
- `*.db` (database files)
- `data/resumes/*` (uploaded resumes)
- `data/generated/*` (generated content)

## Verify Git Status

```bash
# Check what's staged
git status

# View commit history
git log --oneline

# See remote URL
git remote -v
```

## GitHub Repository Recommendations

### Repository Settings

1. **Add Topics**: `python`, `ai`, `resume`, `langchain`, `claude`, `streamlit`, `job-search`

2. **Enable Features**:
   - Issues (for bug tracking)
   - Projects (for roadmap)
   - Discussions (for community)

3. **Branch Protection** (optional for solo project):
   - Require pull request reviews
   - Require status checks

4. **Create GitHub Actions** (optional):
   - Automated testing
   - Code quality checks
   - Deployment workflows

### README Badge Ideas

Add to top of README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![LangChain](https://img.shields.io/badge/langchain-0.1.0+-purple.svg)
![Claude](https://img.shields.io/badge/claude-sonnet--4-orange.svg)
```

## Next Steps After GitHub Setup

1. **Share Your Project**
   - Add project URL to your portfolio
   - Share on LinkedIn
   - Post in relevant communities

2. **Continuous Development**
   - Create issues for Phase 2 features
   - Use project boards for planning
   - Tag releases (v1.0.0, v1.1.0, etc.)

3. **Collaboration**
   - Accept pull requests
   - Respond to issues
   - Update documentation

## Troubleshooting

### Authentication Issues
```bash
# Use personal access token
git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/ResumeOptimizationAgent.git
```

### Large File Issues
```bash
# Check file sizes
du -h data/resumes/* data/generated/*

# Make sure .gitignore is working
git check-ignore -v data/resumes/test.pdf
```

### Undo Last Commit (before push)
```bash
git reset --soft HEAD~1
```

## Current Git Status

Run this to see the current state:

```bash
git status
git log --oneline
git remote -v
```

---

**Ready to push to GitHub!** Follow the steps above to get your project online.
