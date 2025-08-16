import asyncio
import os
from loguru import logger
from dotenv import load_dotenv

from mts.core.config import MTSConfig
from mts.orchestrator import MTSOrchestrator

# Load environment variables first
load_dotenv()

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    "logs/mts_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="DEBUG",  # Full logging in file
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
)
# Add console output
logger.add(
    lambda msg: print(msg) if not any(x in str(msg) for x in [
        "Starting market data update",
        "Got orderbook",
        "Got recent trades",
        "Got funding rate",
        "Calculated metrics",
        "Starting pattern analysis",
        "Starting risk monitoring",
        "Starting order management cycle"
    ]) else None,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>"
)

async def main():
    """Main entry point for MTS"""
    try:
        logger.info("Starting MTS...")
        
        # Initialize MTSConfig
        config = MTSConfig.from_env()
        
        # Initialize MTSOrchestrator
        orchestrator = MTSOrchestrator(config)
        
        logger.info("MTS system initialized. Starting trading cycles...")
        
        # Start an asyncio loop that repeatedly calls run_trading_cycle()
        while True:
            await orchestrator.run_trading_cycle()
            await asyncio.sleep(config.trading.cycle_interval_seconds) # Use config for interval
            
    except asyncio.CancelledError:
        logger.info("MTS shutdown initiated by user.")
    except Exception as e:
        logger.error(f"❌ Fatal error in MTS main loop: {e}")
        raise

def run():
    """Entry point for running the system"""
    try:
        # Create and run the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt - shutting down...")
    except Exception as e:
        logger.error(f"Fatal error during execution: {e}")
        raise
    finally:
        loop.close()

if __name__ == "__main__":
    run()
