from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class MarketRegime(str, Enum):
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    VOLATILE = "volatile"
    ACCUMULATING = "accumulating"
    DISTRIBUTING = "distributing"

class SignalStrength(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

class PatternType(str, Enum):
    TECHNICAL = "technical"
    FUNDING = "funding"
    VOLUME = "volume"
    ORDERFLOW = "orderflow"
    VOLATILITY = "volatility"
    COMPOSITE = "composite"

class MarketPattern(BaseModel):
    """Identified market pattern"""
    pattern_type: PatternType
    signal: SignalStrength
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    description: str
    confidence: float = Field(ge=0, le=1)
    timeframe: str  # e.g., "5m", "1h", "4h", "1d"
    supporting_data: Dict[str, float]

class MarketCondition(BaseModel):
    """Current market condition analysis"""
    asset: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    current_regime: MarketRegime
    current_price: float
    recent_patterns: List[MarketPattern] = Field(default_factory=list)
    volume_profile: Dict[str, float]
    funding_rate: float
    implied_volatility: Optional[float]
    market_depth: Dict[str, float]  # Price levels -> liquidity
    
    class Config:
        arbitrary_types_allowed = True

class TradingSignal(BaseModel):
    """Trading signal generated from pattern analysis"""
    asset: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str  # "buy" or "sell"
    pattern_triggers: List[MarketPattern]
    regime_context: MarketRegime
    confidence: float = Field(ge=0, le=1)
    timeframe: str
    target_price: float
    stop_loss: float
    description: str
    additional_context: Dict[str, str] = Field(default_factory=dict)

class MarketRegimeChange(BaseModel):
    """Detected change in market regime"""
    asset: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    old_regime: MarketRegime
    new_regime: MarketRegime
    confidence: float = Field(ge=0, le=1)
    triggers: List[str]
    implications: Dict[str, str]

class AnomalyDetection(BaseModel):
    """Detected market anomaly"""
    asset: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    anomaly_type: str
    severity: float = Field(ge=0, le=1)
    description: str
    affected_metrics: List[str]
    raw_data: Dict[str, float]
    is_actionable: bool
    recommended_action: Optional[str]