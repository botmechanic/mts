import adk
from ..core.config import ModelConfig
from ..adk_tools.trading_tools import TradingTools
from ..adk_tools.risk_tools import RiskTools

def create_morpheus_agent(risk_tools: RiskTools, trading_tools: TradingTools, config: ModelConfig) -> adk.Agent:
    """
    Creates an ADK Agent for Morpheus, specializing in risk management.
    """
    return adk.Agent(
        model=config.formatted_name,
        instruction_prompt="""You are Morpheus, a strict risk management officer. Given a trading signal and current portfolio state, your role is to assess the risk. Calculate the appropriate position size and determine if the trade adheres to the portfolio's risk parameters. Your output must be a JSON object containing 'risk_assessment', 'position_size', and 'decision' (GO/NO-GO) keys.""",
        tools=[
            risk_tools,
            trading_tools
        ]
    )
