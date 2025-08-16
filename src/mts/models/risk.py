from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class VolatilityWindow(BaseModel):
    """Volatility analysis over a specific time window"""
    window_size: int = Field(description="Size of the volatility window in minutes")
    volatility: float = Field(description="Calculated volatility for the window")
    timestamp: datetime = Field(description="When this volatility was calculated")
    samples: int = Field(description="Number of price samples used")

class PositionRisk(BaseModel):
    """Risk assessment for a specific position"""
    asset: str = Field(description="Asset being traded (e.g. 'HYPE')")
    position_size: float = Field(description="Current position size")
    entry_price: float = Field(description="Average entry price")
    current_price: float = Field(description="Current market price")
    leverage: float = Field(description="Current leverage used")
    unrealized_pnl: float = Field(description="Unrealized profit/loss")
    liquidation_price: Optional[float] = Field(description="Estimated liquidation price")
    risk_level: RiskLevel = Field(description="Assessed risk level")
    max_drawdown: float = Field(description="Maximum drawdown for this position")
    
    @validator('risk_level')
    def assess_risk_level(cls, v, values):
        """Validate and potentially adjust risk level based on position metrics"""
        if 'leverage' in values and 'max_drawdown' in values:
            if values['leverage'] > 5 or values['max_drawdown'] > 0.1:
                return RiskLevel.EXTREME
            elif values['leverage'] > 3 or values['max_drawdown'] > 0.05:
                return RiskLevel.HIGH
        return v

class RiskMetrics(BaseModel):
    """Comprehensive risk metrics for the portfolio"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_equity: float = Field(description="Total account equity")
    used_margin: float = Field(description="Currently used margin")
    available_margin: float = Field(description="Available margin for trading")
    margin_ratio: float = Field(description="Used margin / Total equity")
    daily_pnl: float = Field(description="Profit/loss for the day")
    positions: Dict[str, PositionRisk] = Field(description="Risk metrics per position")
    volatility_windows: Dict[str, List[VolatilityWindow]] = Field(
        description="Volatility analysis for different timeframes"
    )
    
    @property
    def highest_risk_level(self) -> RiskLevel:
        """Get the highest risk level across all positions"""
        if not self.positions:
            return RiskLevel.LOW
        return max(pos.risk_level for pos in self.positions.values())
    
    @property
    def is_margin_safe(self) -> bool:
        """Check if margin usage is within safe limits"""
        return self.margin_ratio < 0.8  # 80% margin usage limit

class PositionSizing(BaseModel):
    """Position sizing recommendation"""
    asset: str = Field(description="Asset to trade")
    suggested_size: float = Field(description="Suggested position size")
    max_leverage: float = Field(description="Maximum suggested leverage")
    stop_loss_price: float = Field(description="Suggested stop loss price")
    take_profit_price: float = Field(description="Suggested take profit price")
    risk_reward_ratio: float = Field(description="Risk/reward ratio for the trade")
    confidence: float = Field(ge=0, le=1, description="Confidence in the recommendation")
    
    @validator('risk_reward_ratio')
    def validate_risk_reward(cls, v):
        """Validate risk/reward ratio is reasonable"""
        if v < 1.5:
            raise ValueError("Risk/reward ratio must be at least 1.5")
        return v