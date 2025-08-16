import adk
from ..core.config import ModelConfig
from ..adk_tools.trading_tools import TradingTools

def create_trinity_agent(trading_tools: TradingTools, config: ModelConfig) -> adk.Agent:
    """
    Creates an ADK Agent for Trinity, specializing in trade execution.
    """
    return adk.Agent(
        model=config.formatted_name,
        instruction_prompt="""You are Trinity, a trade execution specialist. Your only function is to take a fully approved trading order and execute it using the available tools. You will then monitor the order's status and report back on the execution details. Respond only with a JSON object containing 'status', 'order_id', and 'details' keys.""",
        tools=[
            trading_tools
        ]
    )
