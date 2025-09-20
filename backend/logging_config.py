"""
Hackd Comprehensive Logging System
Centralized logging configuration for 100% debug coverage
"""

import logging
import logging.handlers
import os
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

# Ensure logs directory exists
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

class DebugFormatter(logging.Formatter):
    """Enhanced formatter for comprehensive debug information"""
    
    def format(self, record):
        # Add timestamp, process info, and file location
        record.timestamp = datetime.now().isoformat()
        record.process_id = os.getpid()
        record.thread_id = record.thread if hasattr(record, 'thread') else 'main'
        
        # Format the base message
        formatted = super().format(record)
        
        # Add extra debug context if available
        if hasattr(record, 'extra_data'):
            formatted += f"\n  EXTRA_DATA: {json.dumps(record.extra_data, indent=2)}"
        
        # Add stack trace for errors
        if record.exc_info:
            formatted += f"\n  STACK_TRACE:\n{self.formatException(record.exc_info)}"
        
        return formatted

class ComponentLogger:
    """Component-specific logger with comprehensive debug coverage"""
    
    def __init__(self, component_name: str, log_level: str = "DEBUG"):
        self.component_name = component_name
        self.logger = logging.getLogger(f'hackd.{component_name}')
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create component-specific log file
        log_file = LOGS_DIR / component_name / f"{component_name}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Use enhanced formatter
        formatter = DebugFormatter(
            fmt='%(timestamp)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Create error-specific handler
        error_file = LOGS_DIR / "errors" / f"{component_name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        self.info(f"Logger initialized for component: {component_name}")
    
    def debug(self, message: str, extra_data: Dict[str, Any] = None, **kwargs):
        """Enhanced debug logging with optional extra data"""
        self._log_with_extra(logging.DEBUG, message, extra_data, **kwargs)
    
    def info(self, message: str, extra_data: Dict[str, Any] = None, **kwargs):
        """Enhanced info logging with optional extra data"""
        self._log_with_extra(logging.INFO, message, extra_data, **kwargs)
    
    def warning(self, message: str, extra_data: Dict[str, Any] = None, **kwargs):
        """Enhanced warning logging with optional extra data"""
        self._log_with_extra(logging.WARNING, message, extra_data, **kwargs)
    
    def error(self, message: str, extra_data: Dict[str, Any] = None, exception: Exception = None, **kwargs):
        """Enhanced error logging with optional extra data and exception details"""
        if exception:
            kwargs['exc_info'] = (type(exception), exception, exception.__traceback__)
        self._log_with_extra(logging.ERROR, message, extra_data, **kwargs)
    
    def critical(self, message: str, extra_data: Dict[str, Any] = None, **kwargs):
        """Enhanced critical logging with optional extra data"""
        self._log_with_extra(logging.CRITICAL, message, extra_data, **kwargs)
    
    def _log_with_extra(self, level: int, message: str, extra_data: Dict[str, Any] = None, **kwargs):
        """Internal method to log with extra data"""
        extra = kwargs.get('extra', {})
        if extra_data:
            extra['extra_data'] = extra_data
            kwargs['extra'] = extra
        
        self.logger.log(level, message, **kwargs)

class BusinessLogicLogger:
    """Specialized logger for business logic with 100% coverage requirements"""
    
    def __init__(self, component_name: str):
        self.logger = ComponentLogger(component_name)
        self.component_name = component_name
    
    def log_function_entry(self, function_name: str, args: Dict[str, Any] = None, kwargs_dict: Dict[str, Any] = None):
        """Log function entry with all parameters"""
        data = {
            'function': function_name,
            'args': args or {},
            'kwargs': kwargs_dict or {},
            'event': 'function_entry'
        }
        self.logger.debug(f"ENTERING {function_name}", extra_data=data)
    
    def log_function_exit(self, function_name: str, result: Any = None, execution_time: float = None):
        """Log function exit with result and execution time"""
        data = {
            'function': function_name,
            'result_type': type(result).__name__ if result is not None else 'None',
            'execution_time_ms': execution_time * 1000 if execution_time else None,
            'event': 'function_exit'
        }
        # Don't log sensitive data, just the type and size
        if hasattr(result, '__len__'):
            data['result_size'] = len(result)
        
        self.logger.debug(f"EXITING {function_name}", extra_data=data)
    
    def log_ai_request(self, ai_service: str, prompt: str, model: str = None, tokens: int = None):
        """Log AI service requests"""
        data = {
            'ai_service': ai_service,
            'model': model,
            'prompt_length': len(prompt),
            'prompt_preview': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'max_tokens': tokens,
            'event': 'ai_request'
        }
        self.logger.info(f"AI REQUEST to {ai_service}", extra_data=data)
    
    def log_ai_response(self, ai_service: str, response_length: int, tokens_used: int = None, cost: float = None):
        """Log AI service responses"""
        data = {
            'ai_service': ai_service,
            'response_length': response_length,
            'tokens_used': tokens_used,
            'estimated_cost': cost,
            'event': 'ai_response'
        }
        self.logger.info(f"AI RESPONSE from {ai_service}", extra_data=data)
    
    def log_github_api_call(self, endpoint: str, username: str = None, repo: str = None, rate_limit_remaining: int = None):
        """Log GitHub API calls"""
        data = {
            'endpoint': endpoint,
            'username': username,
            'repo': repo,
            'rate_limit_remaining': rate_limit_remaining,
            'event': 'github_api_call'
        }
        self.logger.debug(f"GITHUB API: {endpoint}", extra_data=data)
    
    def log_data_processing(self, operation: str, input_size: int, output_size: int = None, processing_time: float = None):
        """Log data processing operations"""
        data = {
            'operation': operation,
            'input_size': input_size,
            'output_size': output_size,
            'processing_time_ms': processing_time * 1000 if processing_time else None,
            'event': 'data_processing'
        }
        self.logger.debug(f"DATA PROCESSING: {operation}", extra_data=data)
    
    def log_matching_calculation(self, target_user: str, candidate_user: str, score: float, components: Dict[str, float]):
        """Log matching score calculations"""
        data = {
            'target_user': target_user,
            'candidate_user': candidate_user,
            'final_score': score,
            'score_components': components,
            'event': 'matching_calculation'
        }
        self.logger.info(f"MATCH SCORE: {target_user} -> {candidate_user} = {score:.3f}", extra_data=data)
    
    # Basic logging methods for compatibility
    def debug(self, message: str, extra_data: Dict[str, Any] = None, **kwargs):
        """Debug level logging"""
        self.logger.debug(message, extra_data=extra_data, **kwargs)
    
    def info(self, message: str, extra_data: Dict[str, Any] = None, **kwargs):
        """Info level logging"""
        self.logger.info(message, extra_data=extra_data, **kwargs)
    
    def warning(self, message: str, extra_data: Dict[str, Any] = None, **kwargs):
        """Warning level logging"""
        self.logger.warning(message, extra_data=extra_data, **kwargs)
    
    def error(self, message: str, extra_data: Dict[str, Any] = None, exception: Exception = None, **kwargs):
        """Error level logging"""
        self.logger.error(message, extra_data=extra_data, exception=exception, **kwargs)

def get_logger(component_name: str) -> ComponentLogger:
    """Get a logger for a specific component"""
    return ComponentLogger(component_name)

def get_business_logger(component_name: str) -> BusinessLogicLogger:
    """Get a business logic logger for comprehensive coverage"""
    return BusinessLogicLogger(component_name)

def log_system_startup():
    """Log system startup information"""
    system_logger = get_logger("system")
    system_logger.info("Hackd system starting up", extra_data={
        'python_version': sys.version,
        'platform': sys.platform,
        'working_directory': os.getcwd(),
        'log_directory': str(LOGS_DIR)
    })

def log_system_shutdown():
    """Log system shutdown information"""
    system_logger = get_logger("system")
    system_logger.info("Hackd system shutting down")

# Initialize logging system
if __name__ != "__main__":
    log_system_startup()