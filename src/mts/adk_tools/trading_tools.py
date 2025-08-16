import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger

from google_adk import Tool, tool_method

from ..core.config import MTSConfig
from ..models.execution import OrderRequest, OrderResult, OrderStatus
from ..models.market import OrderBook, Trade, FundingRate
from mts.services.hyperliquid import HyperliquidService
from ..services.paper_trading import PaperTradingService

class TradingTools(adk.Tool):
    """
    A collection of tools for interacting with trading services, including market data
    retrieval and order execution.
    """
    def __init__(self, config: MTSConfig):
        self.config = config
        self.hyperliquid_service = HyperliquidService(config)
        self.paper_trading_service = PaperTradingService(self.hyperliquid_service)
        
        # Initialize HyperliquidService asynchronously
        asyncio.create_task(self.hyperliquid_service.initialize())

    @adk.tool_method
    async def get_market_info(self, asset: str) -> Dict[str, Any]:
        """
        Retrieves comprehensive market information for a given asset.

        Args:
            asset: The symbol of the asset (e.g., "BTC", "ETH", "HYPE").

        Returns:
            A dictionary containing market data such as mark price, index price,
            open interest, 24h volume, funding rate, and last update timestamp.
        """
        return await self.hyperliquid_service.get_market_info(asset)

    @adk.tool_method
    async def get_order_book(self, asset: str) -> OrderBook:
        """
        Retrieves the current order book (bids and asks) for a specified asset.

        Args:
            asset: The symbol of the asset.

        Returns:
            An OrderBook object containing lists of bids and asks with their prices and quantities.
        """
        return await self.hyperliquid_service.get_order_book(asset)

    @adk.tool_method
    async def get_recent_trades(self, asset: str, limit: int = 100) -> List[Trade]:
        """
        Retrieves a list of recent trades for a given asset.

        Args:
            asset: The symbol of the asset.
            limit: The maximum number of recent trades to retrieve (default is 100).

        Returns:
            A list of Trade objects, each representing a recent trade.
        """
        return await self.hyperliquid_service.get_recent_trades(asset, limit)

    @adk.tool_method
    async def get_funding_rate(self, asset: str) -> FundingRate:
        """
        Retrieves the current funding rate for a specified asset.

        Args:
            asset: The symbol of the asset.

        Returns:
            A FundingRate object containing the asset, timestamp, and the funding rate.
        """
        return await self.hyperliquid_service.get_funding_rate(asset)

    @adk.tool_method
    async def execute_order(self, order_request: Dict[str, Any]) -> OrderResult:
        """
        Executes a trading order based on the provided order request.

        Args:
            order_request: A dictionary containing the order details.
                           Expected keys: 'asset', 'side', 'order_type', 'quantity', 'price' (optional).
                           Example: {"asset": "BTC", "side": "buy", "order_type": "limit", "quantity": 0.001, "price": 70000}

        Returns:
            An OrderResult object detailing the outcome of the order execution.
        """
        try:
            # Convert dictionary to OrderRequest Pydantic model
            order = OrderRequest(**order_request)
            return await self.paper_trading_service.execute_order(order)
        except Exception as e:
            logger.error(f"Failed to execute order: {e}")
            return OrderResult(
                request=OrderRequest(asset="", side="buy", order_type="market", quantity=0),
                order_id="",
                status=OrderStatus.REJECTED,
                error_message=str(e)
            )

    @adk.tool_method
    async def get_position(self, asset: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the current trading position for a specified asset.

        Args:
            asset: The symbol of the asset.

        Returns:
            A dictionary representing the current position (size, entry price, PnL, etc.),
            or None if no position exists for the asset.
        """
        return await self.paper_trading_service.get_position(asset)

    @adk.tool_method
    async def get_order_status(self, order_id: str) -> OrderResult:
        """
        Retrieves the status of a previously placed order.

        Args:
            order_id: The unique identifier of the order.

        Returns:
            An OrderResult object containing the current status of the order.
        """
        return await self.paper_trading_service.get_order_status(order_id)
