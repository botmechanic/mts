import asyncio
import json
from loguru import logger

from mts.core.config import MTSConfig
from mts.adk_tools.trading_tools import TradingTools
from mts.adk_tools.risk_tools import RiskTools
from ..adk_agents.oracle_agent import create_oracle_agent
from ..adk_agents.neo_agent import create_neo_agent
from ..adk_agents.morpheus_agent import create_morpheus_agent
from ..adk_agents.trinity_agent import create_trinity_agent

class MTSOrchestrator:
    """
    The central orchestrator for the MTS trading system, managing the flow
    between specialized ADK agents.
    """

    def __init__(self, config: MTSConfig):
        self.config = config

        # Initialize Tools
        self.trading_tools = TradingTools(config)
        self.risk_tools = RiskTools()

        # Initialize ADK Agents
        self.oracle_agent = create_oracle_agent(self.trading_tools, config.agent.model)
        self.neo_agent = create_neo_agent(self.trading_tools, config.agent.model)
        self.morpheus_agent = create_morpheus_agent(self.risk_tools, self.trading_tools, config.agent.model)
        self.trinity_agent = create_trinity_agent(self.trading_tools, config.agent.model)

        logger.info("MTSOrchestrator initialized with ADK agents and tools.")

    async def run_trading_cycle(self):
        """
        Executes a single trading analysis and execution cycle.
        """
        logger.info("Starting new trading cycle...")
        target_asset = self.config.trading.default_asset

        try:
            # 1. Oracle: Analyze market conditions
            logger.info(f"Oracle: Analyzing market conditions for {target_asset}...")
            oracle_raw_response = await self.oracle_agent.run(
                f"Analyze the current market conditions for our target asset, {target_asset}."
            )
            oracle_response = json.loads(oracle_raw_response)
            logger.info(f"Oracle Response: {oracle_response}")

            # 2. Neo: Identify patterns and generate trading signal
            logger.info("Neo: Identifying patterns and generating trading signal...")
            neo_raw_response = await self.neo_agent.run(
                f"Market analysis is as follows: {oracle_response.get('summary', '')}. Identify patterns and generate a clear, actionable trading signal (BUY, SELL, or HOLD) with a confidence score."
            )
            neo_response = json.loads(neo_raw_response)
            logger.info(f"Neo Response: {neo_response}")

            # 3. Decision: If Neo indicates a BUY or SELL signal
            signal = neo_response.get('signal', '').upper()
            if signal in ["BUY", "SELL"]:
                logger.info("Trading signal detected. Proceeding to Morpheus for risk assessment.")

                # Get current portfolio status for Morpheus
                current_position = await self.trading_tools.get_position(target_asset)
                total_equity = current_position.get('unrealized_pnl', 0) + current_position.get('realized_pnl', 0) if current_position else 10000 # Placeholder if no position
                risk_percentage = self.config.risk.position_size_pct

                morpheus_prompt = (
                    f"Current portfolio equity is ${total_equity:.2f}. "
                    f"Given the trading signal: {neo_response}, assess the risk using a {risk_percentage * 100}% risk parameter. "
                    f"Current position for {target_asset}: {current_position}."
                )

                # 4. Morpheus: Assess risk and determine go/no-go decision
                logger.info("Morpheus: Assessing risk and determining go/no-go decision...")
                morpheus_raw_response = await self.morpheus_agent.run(morpheus_prompt)
                morpheus_response = json.loads(morpheus_raw_response)
                logger.info(f"Morpheus Response: {morpheus_response}")

                # 5. Decision: If Morpheus gives a "go"
                if morpheus_response.get('decision', '').upper() == "GO":
                    logger.info("Risk assessment approved. Proceeding to Trinity for trade execution.")

                    # 6. Trinity: Execute the approved trade
                    logger.info("Trinity: Executing approved trade...")
                    trinity_raw_response = await self.trinity_agent.run(
                        f"Execute the approved trade: {morpheus_response}."
                    )
                    trinity_response = json.loads(trinity_raw_response)
                    logger.info(f"Trinity Response: {trinity_response}")
                else:
                    logger.warning("Morpheus: Trade not approved due to risk assessment.")
            else:
                logger.info("Neo: No clear BUY or SELL signal. Holding position.")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in agent response: {e}. Raw response: {e.doc}")
        except Exception as e:
            logger.error(f"Error during trading cycle: {e}")