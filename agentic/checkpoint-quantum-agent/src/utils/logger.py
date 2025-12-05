"""Structured logging configuration for the Check Point Quantum Agent."""

import sys
import json
import structlog
from typing import Any, Dict, Optional
from pathlib import Path

from .config import config


def configure_logging() -> None:
    """Configure structured logging for the application."""
    logging_config = config.get_logging_config()
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if logging_config['format'] == 'json' 
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    import logging
    
    # Set log level
    log_level = getattr(logging, logging_config['level'].upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        stream=sys.stdout,
    )
    
    # Add file handler if configured
    if logging_config.get('file'):
        file_handler = logging.FileHandler(logging_config['file'])
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class ActionLogger:
    """Logger for tracking agent actions and API calls."""
    
    def __init__(self, agent_name: str):
        self.logger = get_logger(f"agent.{agent_name}")
        self.agent_name = agent_name
    
    def log_action_start(self, action: str, **kwargs) -> None:
        """Log the start of an action."""
        self.logger.info(
            "Action started",
            agent=self.agent_name,
            action=action,
            **kwargs
        )
    
    def log_action_success(self, action: str, result: Any = None, **kwargs) -> None:
        """Log successful completion of an action."""
        self.logger.info(
            "Action completed successfully",
            agent=self.agent_name,
            action=action,
            result=result,
            **kwargs
        )
    
    def log_action_error(self, action: str, error: str, **kwargs) -> None:
        """Log an action error."""
        self.logger.error(
            "Action failed",
            agent=self.agent_name,
            action=action,
            error=error,
            **kwargs
        )
    
    def log_api_call(self, method: str, endpoint: str, status_code: int, 
                    response_time: float, **kwargs) -> None:
        """Log an API call."""
        self.logger.info(
            "API call",
            agent=self.agent_name,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            response_time=response_time,
            **kwargs
        )
    
    def log_user_command(self, command: str, parsed_intent: Dict[str, Any]) -> None:
        """Log a user command and its parsed intent."""
        self.logger.info(
            "User command processed",
            agent=self.agent_name,
            original_command=command,
            parsed_intent=parsed_intent
        )


class MetricsLogger:
    """Logger for tracking metrics and performance."""
    
    def __init__(self):
        self.logger = get_logger("metrics")
    
    def log_command_processed(self, command_type: str, duration: float, success: bool) -> None:
        """Log command processing metrics."""
        self.logger.info(
            "Command processed",
            command_type=command_type,
            duration=duration,
            success=success
        )
    
    def log_api_metrics(self, endpoint: str, method: str, duration: float, 
                       status_code: int) -> None:
        """Log API performance metrics."""
        self.logger.info(
            "API metrics",
            endpoint=endpoint,
            method=method,
            duration=duration,
            status_code=status_code
        )
    
    def log_agent_metrics(self, agent_name: str, task_type: str, duration: float, 
                         success: bool) -> None:
        """Log agent performance metrics."""
        self.logger.info(
            "Agent metrics",
            agent_name=agent_name,
            task_type=task_type,
            duration=duration,
            success=success
        )


# Initialize logging on module import
configure_logging()

