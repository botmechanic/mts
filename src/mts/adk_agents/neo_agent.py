import adk
from ..core.config import ModelConfig
from ..adk_tools.trading_tools import TradingTools

def create_neo_agent(trading_tools: TradingTools, config: ModelConfig) -> adk.Agent:
    """
    Creates an ADK Agent for Neo, specializing in technical analysis and pattern recognition.
    """
    return adk.Agent(
        model=config.formatted_name,
        instruction_prompt="""You are Neo, an expert in technical analysis and pattern recognition. Based on the market analysis provided to you, your job is to identify classical and novel trading patterns and generate a clear, actionable trading signal (BUY, SELL, or HOLD) with a confidence score. Respond only with a JSON object containing 'signal', 'confidence', and 'reasoning' keys.""",
        tools=[
            trading_tools
        ]
    )
