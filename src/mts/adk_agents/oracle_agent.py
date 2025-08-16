import adk
from ..core.config import ModelConfig
from ..adk_tools.trading_tools import TradingTools

def create_oracle_agent(trading_tools: TradingTools, config: ModelConfig) -> adk.Agent:
    """
    Creates an ADK Agent for the Oracle, specializing in market analysis.
    """
    return adk.Agent(
        model=config.formatted_name,
        instruction_prompt="""You are the Oracle, a quantitative financial analyst. Your sole purpose is to analyze market data using the provided tools to generate price predictions and a comprehensive market summary. Respond only with a JSON object containing 'prediction', 'summary', and 'confidence' keys.""",
        tools=[
            trading_tools
        ]
    )
