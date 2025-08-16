"""Main configuration for MTS"""
import os
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, SecretStr, ConfigDict, field_validator
from loguru import logger
HL_TESTNET_API_URL = "https://api.hyperliquid.xyz/" # Default testnet API URL
HL_MAINNET_API_URL = "https://api.hyperliquid.xyz/" # Default mainnet API URL

class ModelConfig(BaseModel):
    """Model-specific configuration"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    provider: Literal["anthropic", "google"] = Field(
        "anthropic",
        description="AI model provider",
    )
    model_name: str = Field(
        "anthropic:claude-3-5-sonnet-latest",
        description="Model name/version"
    )
    api_key: SecretStr = Field(
        ...,
        description="API key for the model provider"
    )
    temperature: float = Field(0.7, description="Model temperature")
    max_tokens: int = Field(4096, description="Maximum tokens per request")
    top_p: float = Field(0.9, description="Top p sampling parameter")

    @property
    def formatted_name(self) -> str:
        """Get properly formatted model name for PydanticAI"""
        # Return the full model name with provider prefix
        if ':' not in self.model_name:
            return f"{self.provider}:{self.model_name}"
        return self.model_name

    @field_validator('model_name')
    def validate_model_name(cls, v, values):
        """Validate model name is supported"""
        valid_prefixes = ['openai:', 'google:', 'anthropic:']
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(f"Model name must start with one of {valid_prefixes}")
        
        # Additional validation for Anthropic models
        if values.get('provider') == 'anthropic':
            valid_models = [
                "claude-3-5-sonnet-latest",
                "claude-3-haiku",
                "claude-3-opus",
                "claude-2.1"
            ]
            _, model = v.split(':', 1)
            if model not in valid_models:
                raise ValueError(f"Invalid Anthropic model. Must be one of: {valid_models}")
        
        # Additional validation for Google models
        if values.get('provider') == 'google':
            valid_models = [
                "gemini-1.5-flash-latest",
                "gemini-1.5-pro-latest",
                "gemini-pro"
            ]
            _, model = v.split(':', 1)
            if model not in valid_models:
                raise ValueError(f"Invalid Google model. Must be one of: {valid_models}")
        return v

class HyperliquidConfig(BaseModel):
    """Hyperliquid connection configuration"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    account_address: str
    secret_key: SecretStr
    is_testnet: bool = True
    base_position: float = 1.0
    max_position: float = 5.0
    leverage: int = 3
    
    @property
    def api_url(self) -> str:
        return HL_TESTNET_API_URL if self.is_testnet else HL_MAINNET_API_URL

class RiskConfig(BaseModel):
    """Risk management parameters"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    max_drawdown: float = Field(0.02, description="Maximum allowed drawdown")
    stop_loss: float = Field(0.02, description="Default stop loss percentage")
    take_profit: float = Field(0.04, description="Default take profit percentage")
    max_leverage: int = Field(3, description="Maximum allowed leverage")
    position_size_pct: float = Field(0.1, description="Position size as percentage of portfolio")

class TradingConfig(BaseModel):
    """Trading parameters"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    default_asset: str = "HYPE"
    cycle_interval_seconds: int = Field(60, description="Interval in seconds for the trading cycle loop")
    min_spread: float = 0.002
    min_order_interval: int = 30
    volatility_window: int = 100
    max_open_orders: int = 4
    max_position: float = Field(5.0, description="Maximum position size")

class AgentConfig(BaseModel):
    """Agent-specific configuration"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    model: ModelConfig
    system_prompt: str = "You are MTS, an autonomous trading agent..."

class MTSConfig(BaseModel):
    """Main configuration class"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    hyperliquid: HyperliquidConfig
    risk: RiskConfig = RiskConfig()
    trading: TradingConfig = TradingConfig()
    agent: AgentConfig
    debug_mode: bool = False
    
    @classmethod
    def from_env(cls) -> 'MTSConfig':
        """Create configuration from environment variables"""
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Print environment variables for debugging (excluding sensitive data)
        env_vars = {k: v for k, v in os.environ.items() 
                if k.startswith(('HL_', 'DEBUG_')) and 'KEY' not in k}
        logger.debug(f"Environment variables: {env_vars}")
        
        # Validate required environment variables
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        google_api_key = os.getenv("GOOGLE_API_KEY")

        if not anthropic_api_key and not google_api_key:
            raise ValueError("Either ANTHROPIC_API_KEY or GOOGLE_API_KEY must be set.")

        if anthropic_api_key:
            model_provider = "anthropic"
            model_name = os.getenv("HL_ANTHROPIC_MODEL_NAME", "anthropic:claude-3-5-sonnet-latest")
            api_key = SecretStr(anthropic_api_key)
        elif google_api_key:
            model_provider = "google"
            model_name = os.getenv("HL_GOOGLE_MODEL_NAME", "google:gemini-1.5-flash-latest")
            api_key = SecretStr(google_api_key)
        else:
            raise ValueError("No valid AI model API key found.")

        # Validate required environment variables for Hyperliquid
        required_hl_vars = {
            "HL_ACCOUNT_ADDRESS": os.getenv("HL_ACCOUNT_ADDRESS"),
            "HL_SECRET_KEY": os.getenv("HL_SECRET_KEY")
        }
        
        missing_hl_vars = [k for k, v in required_hl_vars.items() if not v]
        if missing_hl_vars:
            raise ValueError(f"Missing required Hyperliquid environment variables: {', '.join(missing_hl_vars)}")
        
        # Log config creation
        logger.info("Creating MTSConfig from environment variables")
        
        model_config = ModelConfig(
            provider=model_provider,
            model_name=model_name,
            api_key=api_key,
            temperature=float(os.getenv("HL_MODEL_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("HL_MODEL_MAX_TOKENS", "4096")),
            top_p=float(os.getenv("HL_MODEL_TOP_P", "0.9"))
        )
        
        config = cls(
            hyperliquid=HyperliquidConfig(
                account_address=os.getenv("HL_ACCOUNT_ADDRESS"),
                secret_key=SecretStr(os.getenv("HL_SECRET_KEY", "")),
                is_testnet=os.getenv("HL_TESTNET", "true").lower() == "true",
                base_position=float(os.getenv("HL_BASE_POSITION", "1.0")),
                max_position=float(os.getenv("HL_MAX_POSITION", "5.0")),
                leverage=int(os.getenv("HL_LEVERAGE", "3"))
            ),
            agent=AgentConfig(
                model=model_config,
                system_prompt=os.getenv(
                    "AGENT_SYSTEM_PROMPT",
                    "You are MTS, an autonomous trading agent..."
                )
            ),
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true"
        )
        
        # Log successful config creation (excluding sensitive data)
        logger.debug(f"Created config: {config.model_dump(exclude={'hyperliquid.secret_key', 'agent.model.api_key'})}")
        
        return config