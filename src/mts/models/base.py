"""Base models and enums for MTS system"""
from enum import Enum

class SystemRole(str, Enum):
    """System role types"""
    OPERATOR = "operator"
    TRADER = "trader"
    ANALYZER = "analyzer"
    RISK_MANAGER = "risk_manager"
    EXECUTOR = "executor"

class SystemStatus(str, Enum):
    """System operational status"""
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class AgentStatus(str, Enum):
    """Agent operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    INITIALIZING = "initializing"

class CommandType(str, Enum):
    """System command types"""
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    RESTART = "restart"
    UPDATE_CONFIG = "update_config"
    EMERGENCY_STOP = "emergency_stop"

class SystemEventType(str, Enum):
    """System event types"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    TRADE = "trade"
    METRIC = "metric"
    AGENT = "agent"