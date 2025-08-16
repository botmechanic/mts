from google_adk import Tool, tool_method
from loguru import logger

class RiskTools(adk.Tool):
    """
    A collection of tools for risk management calculations.
    """

    @adk.tool_method
    def calculate_position_size(self, asset: str, price: float, total_equity: float, risk_percentage: float) -> float:
        """
        Calculates the safe position size for a given asset based on risk parameters.

        Args:
            asset: The symbol of the asset (e.g., "BTC", "ETH").
            price: The current price of the asset.
            total_equity: The total equity available in the trading account.
            risk_percentage: The percentage of total equity to risk per trade (e.g., 0.01 for 1%).

        Returns:
            The calculated position size in units of the asset.
        """
        try:
            if price <= 0 or total_equity <= 0 or risk_percentage <= 0:
                logger.warning("Invalid input for position size calculation. Price, total_equity, and risk_percentage must be positive.")
                return 0.0

            max_position_value = total_equity * risk_percentage
            position_size = max_position_value / price
            return position_size
        except Exception as e:
            logger.error(f"Error calculating position size for {asset}: {e}")
            return 0.0
