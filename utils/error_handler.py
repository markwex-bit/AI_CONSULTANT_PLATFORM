import logging
import traceback
from typing import Dict, Any, Optional
from flask import jsonify, request
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base application error class"""
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"ERR_{status_code}"

class ValidationError(AppError):
    """Validation error"""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, 400, "VALIDATION_ERROR")
        self.field = field

class DatabaseError(AppError):
    """Database error"""
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, 500, "DATABASE_ERROR")
        self.operation = operation

class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(self, message: str, resource: str = None):
        super().__init__(message, 404, "NOT_FOUND")
        self.resource = resource

def handle_errors(f):
    """Decorator to handle errors in API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError as e:
            logger.error(f"Application error: {e.message}", exc_info=True)
            return jsonify({
                'success': False,
                'error': e.message,
                'error_code': e.error_code,
                'status_code': e.status_code
            }), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'error_code': 'INTERNAL_ERROR',
                'status_code': 500
            }), 500
    return decorated_function

def log_request_info():
    """Log request information for debugging"""
    logger.info(f"Request: {request.method} {request.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    if request.json:
        logger.info(f"Body: {request.json}")

def log_response_info(response):
    """Log response information for debugging"""
    logger.info(f"Response: {response.status_code}")
    return response

def setup_error_handlers(app):
    """Setup Flask error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found',
            'error_code': 'NOT_FOUND',
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'error_code': 'METHOD_NOT_ALLOWED',
            'status_code': 405
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Internal server error", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR',
            'status_code': 500
        }), 500

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Validate that required fields are present in data"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

def validate_field_type(value: Any, expected_type: type, field_name: str) -> None:
    """Validate field type"""
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"Field '{field_name}' must be of type {expected_type.__name__}",
            field_name
        )

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_str(value: Any, default: str = "") -> str:
    """Safely convert value to string"""
    return str(value) if value is not None else default
