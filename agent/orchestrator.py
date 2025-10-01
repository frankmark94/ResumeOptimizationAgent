"""LangChain agent orchestration for resume optimization."""
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from config import settings
from agent.prompts import SYSTEM_PROMPT

# Import all tools
from tools.resume_parser import parse_resume
from tools.job_analyzer import analyze_job_description, extract_job_keywords
from tools.resume_comparator import compare_resume_to_job, calculate_match_score
from tools.resume_optimizer import (
    optimize_resume_section,
    generate_resume_bullets,
    improve_ats_compatibility
)
from tools.session_tools import check_resume_status, get_session_context
from tools.job_search_tools import (
    search_jobs_by_criteria,
    get_job_details,
    filter_jobs_by_requirements,
    list_available_jobs
)
from tools.document_generation_tools import (
    generate_optimized_resume,
    generate_cover_letter,
    list_generated_documents
)


def _parse_claude_output(output: Any) -> str:
    """Parse Claude's output format to extract text content.

    Claude Sonnet 4 with tool calling returns a list of content blocks.
    This function extracts the text from those blocks.
    """
    if isinstance(output, list):
        # Extract text content from list of content blocks
        text_parts = []
        for block in output:
            if isinstance(block, dict) and block.get('type') == 'text':
                text_parts.append(block.get('text', ''))
        return '\n'.join(text_parts) if text_parts else str(output)
    return str(output)


class _AgentExecutorWrapper:
    """Wrapper to parse Claude's output format from AgentExecutor."""

    def __init__(self, executor: AgentExecutor):
        self.executor = executor

    def invoke(self, *args, **kwargs) -> Dict[str, Any]:
        """Synchronous invoke with output parsing."""
        result = self.executor.invoke(*args, **kwargs)
        if 'output' in result:
            result['output'] = _parse_claude_output(result['output'])
        return result

    async def ainvoke(self, *args, **kwargs) -> Dict[str, Any]:
        """Async invoke with output parsing."""
        result = await self.executor.ainvoke(*args, **kwargs)
        if 'output' in result:
            result['output'] = _parse_claude_output(result['output'])
        return result

    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped executor."""
        return getattr(self.executor, name)


def _wrap_agent_executor(executor: AgentExecutor) -> _AgentExecutorWrapper:
    """Wrap an AgentExecutor to handle Claude's output format."""
    return _AgentExecutorWrapper(executor)


def create_career_advisor_agent() -> AgentExecutor:
    """
    Create and configure the career advisor agent with all tools.

    Returns:
        AgentExecutor: Configured agent ready to use
    """
    # Initialize Claude LLM
    llm = ChatAnthropic(
        model=settings.model_name,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens
    )

    # Define all available tools - SESSION TOOLS FIRST for priority
    tools = [
        # Session Context (Priority 1)
        check_resume_status,      # CRITICAL: Check this before asking for resume
        get_session_context,      # Get full session context

        # Resume Tools (Priority 2)
        parse_resume,

        # Job Search Tools (Priority 3)
        search_jobs_by_criteria,
        get_job_details,
        filter_jobs_by_requirements,
        list_available_jobs,

        # Job Analysis Tools (Priority 4)
        analyze_job_description,
        extract_job_keywords,
        compare_resume_to_job,
        calculate_match_score,

        # Resume Optimization Tools (Priority 5)
        optimize_resume_section,
        generate_resume_bullets,
        improve_ats_compatibility,

        # Document Generation Tools (Priority 6)
        generate_optimized_resume,
        generate_cover_letter,
        list_generated_documents,
    ]

    # Create agent prompt - using placeholder syntax as recommended by LangChain docs
    # This ensures proper tool-calling behavior with Claude
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Create the agent - bind_tools is called internally by create_tool_calling_agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # Create memory for conversation history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )

    # Create agent executor with output parser
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=15,  # Increased from 10 to handle multi-step workflows
        max_execution_time=300,  # 5 minutes max
        handle_parsing_errors=True,
        return_intermediate_steps=False,
        early_stopping_method="generate"  # Return partial result instead of error
    )

    # Wrap the agent executor to parse Claude's response format
    return _wrap_agent_executor(agent_executor)


def run_agent(agent_executor: AgentExecutor, user_input: str) -> str:
    """
    Run the agent with user input and return the response.

    Args:
        agent_executor: Configured agent executor
        user_input: User's message/query

    Returns:
        str: Agent's response
    """
    try:
        result = agent_executor.invoke({"input": user_input})
        output = result.get("output", "I apologize, but I encountered an issue processing your request.")

        # Handle Claude's response format - extract text from content blocks if needed
        if isinstance(output, list):
            # Extract text content from list of content blocks
            text_parts = []
            for block in output:
                if isinstance(block, dict) and block.get('type') == 'text':
                    text_parts.append(block.get('text', ''))
            return '\n'.join(text_parts) if text_parts else str(output)

        return output
    except Exception as e:
        return f"Error: {str(e)}\n\nPlease try rephrasing your request or breaking it into smaller steps."


async def arun_agent(agent_executor: AgentExecutor, user_input: str) -> str:
    """
    Async version of run_agent for Streamlit.

    Args:
        agent_executor: Configured agent executor
        user_input: User's message/query

    Returns:
        str: Agent's response
    """
    try:
        result = await agent_executor.ainvoke({"input": user_input})
        output = result.get("output", "I apologize, but I encountered an issue processing your request.")

        # Handle Claude's response format - extract text from content blocks if needed
        if isinstance(output, list):
            # Extract text content from list of content blocks
            text_parts = []
            for block in output:
                if isinstance(block, dict) and block.get('type') == 'text':
                    text_parts.append(block.get('text', ''))
            return '\n'.join(text_parts) if text_parts else str(output)

        return output
    except Exception as e:
        return f"Error: {str(e)}\n\nPlease try rephrasing your request or breaking it into smaller steps."


# Singleton agent instance
_agent_executor = None


def get_agent() -> AgentExecutor:
    """
    Get or create the singleton agent instance.

    Returns:
        AgentExecutor: The career advisor agent
    """
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = create_career_advisor_agent()
    return _agent_executor


def reset_agent():
    """Reset the agent and clear conversation memory."""
    global _agent_executor
    _agent_executor = None
