"""Base agent class with common functionality."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str):
        """Initialize base agent.
        
        Args:
            name: Agent name
        """
        self.name = name
        self.logger = logging.getLogger(f"agents.{name}")
    
    @abstractmethod
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with given payload.
        
        Args:
            payload: Input data
            
        Returns:
            Output data
        """
        pass
    
    def log_start(self, message: str = ""):
        """Log agent start."""
        msg = f"{self.name} agent starting"
        if message:
            msg += f": {message}"
        self.logger.info(msg)
    
    def log_complete(self, message: str = ""):
        """Log agent completion."""
        msg = f"{self.name} agent completed"
        if message:
            msg += f": {message}"
        self.logger.info(msg)
    
    def log_error(self, error: Exception):
        """Log agent error."""
        self.logger.error(f"{self.name} agent error: {error}", exc_info=True)
