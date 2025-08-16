from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict 

class TimeFrame(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"

class MarketDataType(str, Enum):
    TRADE = "trade"
    FUNDING = "funding"
    LIQUIDATION = "liquidation"
    ORDERBOOK = "orderbook"
    INDEX = "index"
    MARK = "mark"

class Candle(BaseModel):
    """Price candlestick data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trades: int
    timeframe: TimeFrame
    
    @property
    def range(self) -> float:
        """Calculate candle range"""
        return self.high - self.low
    
    @property
    def body(self) -> float:
        """Calculate candle body size"""
        return abs(self.close - self.open)
    
    @property
    def is_bullish(self) -> bool:
        """Check if candle is bullish"""
        return self.close > self.open

class OrderBookLevel(BaseModel):
    """Single level in the order book"""
    price: float
    quantity: float
    orders: int = Field(default=1)

class OrderBook(BaseModel):
    """Full order book snapshot"""
    asset: str
    timestamp: datetime
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    
    @property
    def spread(self) -> float:
        """Calculate bid-ask spread"""
        return self.asks[0].price - self.bids[0].price if self.bids and self.asks else 0
    
    @property
    def mid_price(self) -> float:
        """Calculate mid price"""
        return (self.asks[0].price + self.bids[0].price) / 2 if self.bids and self.asks else 0
    
    def imbalance(self, depth: int = 10) -> float:
        """Calculate order book imbalance at given depth"""
        bid_vol = sum(level.quantity for level in self.bids[:depth])
        ask_vol = sum(level.quantity for level in self.asks[:depth])
        total_vol = bid_vol + ask_vol
        return (bid_vol - ask_vol) / total_vol if total_vol > 0 else 0

class Trade(BaseModel):
    """Individual trade data"""
    asset: str
    timestamp: datetime
    price: float
    quantity: float
    side: str  # 'buy' or 'sell'
    liquidation: bool = Field(default=False)
    maker: bool = Field(default=False)
    fee: Optional[float] = None
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

    @classmethod
    def from_hyperliquid(cls, data: dict, asset: str) -> 'Trade':
        """Create Trade from Hyperliquid data"""
        return cls(
            asset=asset,
            timestamp=datetime.fromtimestamp(data.get('time', 0) / 1000, timezone.utc),
            price=float(data.get('px', 0)),
            quantity=float(data.get('sz', 0)),
            side='buy' if data.get('side') == 'B' else 'sell',
            liquidation=bool(data.get('liquidatedUser', False)),
            maker=bool(data.get('maker', False)),
            fee=float(data.get('fee', 0))
        )

    @field_validator('side')
    def validate_side(cls, v):
        if v not in ['buy', 'sell']:
            raise ValueError('side must be either buy or sell')
        return v

class FundingRate(BaseModel):
    """Funding rate data"""
    asset: str
    timestamp: datetime
    rate: float  # hourly rate
    predicted_rate: Optional[float] = None
    
    @field_validator('rate', 'predicted_rate')
    def validate_rate(cls, v):
        if v is not None and abs(v) > 0.01:  # Max 1% per hour
            raise ValueError('Funding rate exceeds normal range')
        return v

class MarketDepth(BaseModel):
    """Market depth analysis"""
    asset: str
    timestamp: datetime
    bid_depth: Dict[float, float]  # price -> cumulative volume
    ask_depth: Dict[float, float]
    
    def impact_price(self, size: float, side: str) -> float:
        """Calculate expected price after market impact"""
        depth = self.ask_depth if side == 'buy' else self.bid_depth
        for price, cum_vol in depth.items():
            if cum_vol >= size:
                return price
        return list(depth.keys())[-1]  # Return worst price if size > liquidity
    
    def liquidity_score(self, price_range: float = 0.01) -> float:
        """Calculate liquidity score within price range"""
        mid_price = min(self.ask_depth.keys())  # First ask price
        upper_bound = mid_price * (1 + price_range)
        lower_bound = mid_price * (1 - price_range)
        
        bid_liquidity = sum(vol for p, vol in self.bid_depth.items() if p >= lower_bound)
        ask_liquidity = sum(vol for p, vol in self.ask_depth.items() if p <= upper_bound)
        
        return (bid_liquidity + ask_liquidity) / 2

class IndexPrice(BaseModel):
    """Index price data"""
    asset: str
    timestamp: datetime
    price: float
    components: Dict[str, float]  # exchange -> price
    
    def deviation_from_component(self, exchange: str) -> float:
        """Calculate deviation from specific exchange price"""
        if exchange in self.components:
            return (self.price - self.components[exchange]) / self.components[exchange]
        return 0

class MarkPrice(BaseModel):
    """Mark price data"""
    asset: str
    timestamp: datetime
    price: float
    index_price: Optional[float] = None
    fair_price: Optional[float] = None
    
    @property
    def premium(self) -> Optional[float]:
        """Calculate premium over index"""
        if self.index_price:
            return (self.price - self.index_price) / self.index_price
        return None

class LiquidationEvent(BaseModel):
    """Liquidation event data"""
    asset: str
    timestamp: datetime
    price: float
    quantity: float
    side: str  # 'long' or 'short'
    pnl: Optional[float] = None
    
    @field_validator('side')
    def validate_side(cls, v):
        if v not in ['long', 'short']:
            raise ValueError('side must be either long or short')
        return v

class MarketSummary(BaseModel):
    """Summary of market state"""
    asset: str
    timestamp: datetime
    mark_price: float
    index_price: float
    funding_rate: float
    open_interest: float
    volume_24h: float
    liquidations_24h: float
    long_short_ratio: float
    volatility_24h: float

class VolumeProfile(BaseModel):
    """Volume profile analysis"""
    asset: str
    timeframe: TimeFrame
    start_time: datetime
    end_time: datetime
    price_levels: Dict[float, float]  # price -> volume
    poc: float = Field(description="Point of Control - price level with highest volume")
    value_area_high: float
    value_area_low: float
    value_area_volume: float = Field(description="Volume within value area")

class MarketData(BaseModel):
    """Combined market data"""
    asset: str
    timestamp: datetime
    candle: Optional[Candle] = None
    orderbook: Optional[OrderBook] = None
    trades: List[Trade] = Field(default_factory=list)
    funding: Optional[FundingRate] = None
    depth: Optional[MarketDepth] = None
    index: Optional[IndexPrice] = None
    mark: Optional[MarkPrice] = None
    liquidations: List[LiquidationEvent] = Field(default_factory=list)
    summary: Optional[MarketSummary] = None
    volume_profile: Optional[VolumeProfile] = None

    def get_price(self, price_type: str = 'mark') -> Optional[float]:
        """Get price by type"""
        if price_type == 'mark' and self.mark:
            return self.mark.price
        elif price_type == 'index' and self.index:
            return self.index.price
        elif price_type == 'mid' and self.orderbook:
            return self.orderbook.mid_price
        elif price_type == 'last' and self.trades:
            return self.trades[-1].price if self.trades else None
        return None

    def get_data_by_type(self, data_type: MarketDataType) -> Union[BaseModel, List[BaseModel], None]:
        """Get specific type of market data"""
        if data_type == MarketDataType.TRADE:
            return self.trades
        elif data_type == MarketDataType.FUNDING:
            return self.funding
        elif data_type == MarketDataType.LIQUIDATION:
            return self.liquidations
        elif data_type == MarketDataType.ORDERBOOK:
            return self.orderbook
        elif data_type == MarketDataType.INDEX:
            return self.index
        elif data_type == MarketDataType.MARK:
            return self.mark
        return None