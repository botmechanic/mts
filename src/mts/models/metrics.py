"""Metrics models for MTS system"""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

class PerformanceMetrics(BaseModel):
    """System performance metrics"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    total_trades: int = Field(default=0)
    successful_trades: int = Field(default=0)
    failed_trades: int = Field(default=0)
    total_pnl: float = Field(default=0)
    win_rate: float = Field(default=0)
    average_trade_duration: float = Field(default=0)
    sharpe_ratio: float = Field(default=0)
    max_drawdown: float = Field(default=0)
    current_drawdown: float = Field(default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('win_rate')
    def validate_win_rate(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Win rate must be between 0 and 1")
        return v

class ResourceMetrics(BaseModel):
    """System resource utilization metrics"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    cpu_usage: float = Field(default=0)
    memory_usage: float = Field(default=0)
    network_latency: float = Field(default=0)
    api_calls_per_minute: int = Field(default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('cpu_usage', 'memory_usage')
    def validate_usage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Usage metrics must be between 0 and 100")
        return v