import asyncio


async def simple_agent_demo():
    thoughts = [
        "Thought: I need to fetch the schema...",
        "Action: Calling DBSchemaTool...",
        "Thought: Now I need to generate SQL...",
        "Action: Executing SQL query...",
        "Result: 250 sales last month"
    ]

    for thought in thoughts:
        await asyncio.sleep(1)
        yield thought
