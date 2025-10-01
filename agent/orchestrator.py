"""LangChain agent orchestration for resume optimization."""
from typing import List
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

    # Define all available tools
    tools = [
        parse_resume,
        analyze_job_description,
        extract_job_keywords,
        compare_resume_to_job,
        calculate_match_score,
        optimize_resume_section,
        generate_resume_bullets,
        improve_ats_compatibility,
    ]

    # Create agent prompt with system message and chat history
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create the agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # Create memory for conversation history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )

    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=10,
        max_execution_time=300,  # 5 minutes max
        handle_parsing_errors=True,
        return_intermediate_steps=False
    )

    return agent_executor


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
        return result.get("output", "I apologize, but I encountered an issue processing your request.")
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
        return result.get("output", "I apologize, but I encountered an issue processing your request.")
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
