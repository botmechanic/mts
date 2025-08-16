from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ExecutionQuality(BaseModel):
    """Metrics for execution quality"""
    slippage: float = Field(description="Price slippage in basis points")
    fill_time: float = Field(description="Time to fill in seconds")
    price_impact: float = Field(description="Market impact in basis points")
    filled_quantity: float = Field(description="Amount filled")
    remaining_quantity: float = Field(description="Amount remaining")
    average_fill_price: float = Field(description="Average fill price")
    fees_paid: float = Field(description="Total fees paid")

class OrderRequest(BaseModel):
    """Request to execute an order"""
    asset: str = Field(description="Asset to trade")
    side: OrderSide
    order_type: OrderType
    quantity: float = Field(gt=0)
    price: Optional[float] = Field(description="Limit price if applicable")
    stop_price: Optional[float] = Field(description="Stop price if applicable")
    reduce_only: bool = Field(default=False)
    post_only: bool = Field(default=False)
    time_in_force: str = Field(default="GTC")
    leverage: Optional[float] = None
    
    @field_validator('price')
    def validate_price(cls, v, values):
        if values['order_type'] in [OrderType.LIMIT, OrderType.STOP_LIMIT] and v is None:
            raise ValueError("Limit orders require a price")
        return v
    
    @field_validator('stop_price')
    def validate_stop_price(cls, v, values):
        if values['order_type'] in [OrderType.STOP_MARKET, OrderType.STOP_LIMIT] and v is None:
            raise ValueError("Stop orders require a stop price")
        return v

class OrderResult(BaseModel):
    """Result of order execution"""
    request: OrderRequest
    order_id: str
    status: OrderStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    filled_quantity: float = 0
    remaining_quantity: float = 0
    average_fill_price: Optional[float] = None
    fees: float = 0
    execution_quality: Optional[ExecutionQuality] = None
    error_message: Optional[str] = None

class PositionManagement(BaseModel):
    """Position management parameters"""
    asset: str
    current_size: float
    entry_price: float
    unrealized_pnl: float
    liquidation_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    trailing_stop: Optional[float]
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ExecutionStrategy(str, Enum):
    AGGRESSIVE = "aggressive"  # Cross the spread for immediate fill
    PASSIVE = "passive"       # Post limit orders
    ADAPTIVE = "adaptive"     # Adjust based on market conditions
    TWAP = "twap"            # Time-weighted average price
    VWAP = "vwap"            # Volume-weighted average price

class ExecutionMetrics(BaseModel):
    """Execution performance metrics"""
    total_filled: float = 0
    total_fees: float = 0
    average_slippage: float = 0
    fill_rate: float = 0  # filled/attempted
    success_rate: float = 0  # successful orders/total orders
    average_fill_time: float = 0
    cost_savings: float = 0  # vs. market impact
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class LiquidityAnalysis(BaseModel):
    """Analysis of available liquidity"""
    asset: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    bid_liquidity: Dict[float, float]  # price -> quantity
    ask_liquidity: Dict[float, float]
    spread: float
    depth_impact: Dict[float, float]  # size -> expected price impact
    recent_trades: List[Dict[str, float]]  # recent trade sizes and prices
    
    def get_optimal_size(self, side: OrderSide, max_impact: float) -> float:
        """Calculate optimal order size given max acceptable price impact"""
        liquidity = self.ask_liquidity if side == OrderSide.BUY else self.bid_liquidity
        for size, impact in self.depth_impact.items():
            if impact > max_impact:
                return size - 1  # Return size just below impact threshold
        return max(liquidity.values())  # Return max available if impact acceptable