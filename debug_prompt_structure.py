#!/usr/bin/env python3
"""
Debug script to inspect the exact prompt structure sent to Claude.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_tool_calling_agent
from config import settings
from agent.prompts import SYSTEM_PROMPT

# Simple test tool
@tool
def parse_resume(file_path: str) -> str:
    """Parse a resume file and extract structured information.

    Args:
        file_path: Path to the resume file
    """
    return f"Parsed resume at {file_path}"

def debug_prompt():
    """Debug the prompt structure."""
    print("=" * 80)
    print("DEBUGGING PROMPT STRUCTURE")
    print("=" * 80)
    print()

    # Create prompt using the new syntax
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    print("1. SYSTEM PROMPT:")
    print("-" * 80)
    print(SYSTEM_PROMPT)
    print("-" * 80)
    print()

    print("2. PROMPT STRUCTURE:")
    print("-" * 80)
    print(f"Input variables: {prompt.input_variables}")
    print(f"Partial variables: {prompt.partial_variables}")
    print(f"Message types: {[type(m).__name__ for m in prompt.messages]}")
    print("-" * 80)
    print()

    print("3. FORMATTED PROMPT (with test input):")
    print("-" * 80)
    test_values = {
        "input": "Please parse my resume at: /home/test/resume.pdf",
        "chat_history": [],
        "agent_scratchpad": []
    }
    formatted = prompt.format_messages(**test_values)
    for i, msg in enumerate(formatted, 1):
        print(f"Message {i} ({type(msg).__name__}):")
        print(f"  Role: {msg.type if hasattr(msg, 'type') else 'unknown'}")
        content = str(msg.content)
        if len(content) > 200:
            content = content[:200] + "..."
        print(f"  Content: {content}")
        print()
    print("-" * 80)
    print()

    # Now test with the actual agent
    print("4. TESTING WITH REAL AGENT:")
    print("-" * 80)

    try:
        # Create LLM and agent
        llm = ChatAnthropic(
            model=settings.model_name,
            anthropic_api_key=settings.anthropic_api_key if hasattr(settings, 'anthropic_api_key') else 'dummy',
            temperature=0.0,
        )

        tools = [parse_resume]

        # This is what create_tool_calling_agent does internally
        print("Tools being bound to LLM:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:80]}...")

        # Create agent
        agent = create_tool_calling_agent(llm, tools, prompt)

        print()
        print("✓ Agent created successfully")
        print(f"  Agent type: {type(agent)}")
        print()

        # Show what gets passed to the LLM
        print("5. WHAT CLAUDE SEES:")
        print("-" * 80)
        print("When user says: 'Please parse my resume at: /path/to/file.pdf'")
        print()
        print("Claude receives:")
        print("  1. System message with role='system'")
        print("  2. User message with role='user': 'Please parse my resume at: /path/to/file.pdf'")
        print("  3. Tools available: parse_resume (and others)")
        print()
        print("Expected behavior:")
        print("  → Claude should invoke: parse_resume(file_path='/path/to/file.pdf')")
        print("-" * 80)

    except Exception as e:
        print(f"Error creating agent: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    debug_prompt()
