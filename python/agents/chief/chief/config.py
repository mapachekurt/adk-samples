from ADK.config import agents

# The unique name of your agent.
def name() -> str:
    return "chief"

# The top-level instructions for your agent.
def instructions() -> str:
    from . import prompts
    return prompts.INSTRUCTION

# The tools that your agent has access to.
def tools() -> list:
    return []

# The sub-agents that your agent has access to.
def sub_agents() -> list:
    return []

# The final compiled agent.
def agent():
    return agents.gen_agent(
        name=name(),
        instructions=instructions(),
        tools=tools(),
        sub_agents=sub_agents(),
    )
