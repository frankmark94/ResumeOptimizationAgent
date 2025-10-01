"""Test script to verify response parsing fix."""
import asyncio
from agent.orchestrator import create_career_advisor_agent

async def test_response_format():
    """Test that agent responses are properly formatted."""
    print("="*80)
    print("Testing Response Format Fix")
    print("="*80)

    agent = create_career_advisor_agent()

    test_input = "Please parse my resume at: /home/frankmark94/ResumeOptimizationAgent/data/resumes/resume_20251001_054049.pdf"

    print(f"\nInput: {test_input}\n")
    print("Invoking agent...\n")

    result = await agent.ainvoke({"input": test_input})
    output = result.get("output")

    print(f"Output type: {type(output)}")
    print(f"Output is list: {isinstance(output, list)}")

    if isinstance(output, list):
        print(f"\n❌ ERROR: Output is still a list!")
        print(f"List length: {len(output)}")
        print(f"First item: {output[0] if output else 'empty'}")
    else:
        print(f"\n✅ SUCCESS: Output is a string!")
        print(f"\nFirst 500 characters:")
        print("-" * 80)
        print(output[:500])
        print("-" * 80)

    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_response_format())
