import logging
import json
from datetime import datetime
from typing import Any, Dict
from fastapi import Request
import uuid

class CustomJSONFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.default_fields = {
            'timestamp': '',
            'level': '',
            'message': '',
            'request_id': '',
            'endpoint': '',
            'method': '',
            'status_code': '',
            'execution_time': '',
        }

    def format(self, record: logging.LogRecord) -> str:
        json_record: Dict[str, Any] = {}
        json_record.update(self.default_fields)
        
        # Add basic log record attributes
        json_record['timestamp'] = datetime.utcnow().isoformat()
        json_record['level'] = record.levelname
        json_record['message'] = record.getMessage()
        
        # Add extra fields from the record
        if hasattr(record, 'request_id'):
            json_record['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            json_record['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            json_record['method'] = record.method
        if hasattr(record, 'status_code'):
            json_record['status_code'] = record.status_code
        if hasattr(record, 'execution_time'):
            json_record['execution_time'] = record.execution_time
        
        return json.dumps(json_record)

def setup_logging():
    logger = logging.getLogger("service_logger")
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomJSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler for Filebeat
    file_handler = logging.FileHandler("/var/log/service/service.log")
    file_handler.setFormatter(CustomJSONFormatter())
    logger.addHandler(file_handler)
    
    return logger

# Create a global logger instance
logger = setup_logging()

def get_request_id() -> str:
    return str(uuid.uuid4())

async def log_request_middleware(request: Request, call_next):
    request_id = get_request_id()
    start_time = datetime.utcnow()
    
    # Add request_id to request state
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    # Calculate execution time
    execution_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Log the request details
    logger.info(
        f"Request processed",
        extra={
            'request_id': request_id,
            'endpoint': str(request.url.path),
            'method': request.method,
            'status_code': response.status_code,
            'execution_time': execution_time
        }
    )
    
    # Add request ID to response headers
    response.headers['X-Request-ID'] = request_id
    return response 
