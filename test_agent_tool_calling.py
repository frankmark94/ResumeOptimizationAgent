#!/usr/bin/env python3
"""
Test script to verify the agent properly calls tools.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.orchestrator import create_career_advisor_agent
from config import settings

def test_parse_resume_tool_calling():
    """Test that the agent calls parse_resume when given a file path."""
    print("=" * 80)
    print("TESTING: Agent Tool-Calling for parse_resume")
    print("=" * 80)
    print()

    # Create agent
    print("Creating agent...")
    agent = create_career_advisor_agent()
    print("✓ Agent created successfully")
    print()

    # Test input with explicit file path
    test_input = "Please parse my resume at: /home/frankmark94/ResumeOptimizationAgent/data/resumes/resume_20251001_054049.pdf"

    print("User input:")
    print(f"  {test_input}")
    print()

    print("Invoking agent with verbose=True...")
    print("-" * 80)

    try:
        result = agent.invoke({"input": test_input})

        print("-" * 80)
        print()
        print("=" * 80)
        print("RESULT:")
        print("=" * 80)
        print(result.get("output", "No output"))
        print()

        # Check if intermediate steps show tool calls
        if "intermediate_steps" in result:
            print("=" * 80)
            print("INTERMEDIATE STEPS:")
            print("=" * 80)
            for i, step in enumerate(result["intermediate_steps"], 1):
                print(f"Step {i}: {step}")
            print()

        print("=" * 80)
        print("TEST COMPLETED")
        print("=" * 80)

    except Exception as e:
        print("-" * 80)
        print()
        print("=" * 80)
        print("ERROR:")
        print("=" * 80)
        print(f"{type(e).__name__}: {e}")
        print()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if API key is set
    if not settings.anthropic_api_key or settings.anthropic_api_key == "your-api-key-here":
        print("ERROR: ANTHROPIC_API_KEY not set in environment or .env file")
        print("Please set your Anthropic API key before running this test.")
        sys.exit(1)

    test_parse_resume_tool_calling()
