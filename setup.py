"""
Setup script for Resume Optimization Agent
Initializes database and verifies environment
"""
import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.10 or higher."""
    if sys.version_info < (3, 10):
        print("❌ Error: Python 3.10 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  Warning: .env file not found")
        print("Creating .env from .env.example...")
        example_path = Path(".env.example")
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            print("✅ Created .env file")
            print("⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY")
            return False
        else:
            print("❌ Error: .env.example not found")
            return False
    print("✅ .env file exists")
    return True


def check_api_key():
    """Check if Anthropic API key is configured."""
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_anthropic_api_key_here":
        print("❌ Error: ANTHROPIC_API_KEY not configured in .env")
        print("Get your API key at: https://console.anthropic.com")
        return False
    print("✅ Anthropic API key configured")
    return True


def create_directories():
    """Create necessary directories."""
    dirs = [
        "data",
        "data/resumes",
        "data/generated"
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    print("✅ Created data directories")
    return True


def initialize_database():
    """Initialize SQLite database."""
    try:
        from models.database import init_db
        init_db()
        print("✅ Database initialized")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        "langchain",
        "langchain_anthropic",
        "streamlit",
        "sqlalchemy",
        "pydantic",
        "PyPDF2",
        "docx"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("✅ All required packages installed")
    return True


def main():
    """Run setup checks."""
    print("\n" + "="*50)
    print("Resume Optimization Agent - Setup")
    print("="*50 + "\n")

    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("API Key", check_api_key),
        ("Directories", create_directories),
        ("Database", initialize_database),
    ]

    results = []
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        result = check_func()
        results.append((name, result))

    # Summary
    print("\n" + "="*50)
    print("Setup Summary")
    print("="*50)

    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False

    print("\n")

    if all_passed:
        print("🎉 Setup complete! You're ready to use the agent.")
        print("\nTo start the application, run:")
        print("  streamlit run app.py")
    else:
        print("⚠️  Setup incomplete. Please address the errors above.")

    print("\n")


if __name__ == "__main__":
    main()
