# config.py - Configuration settings
import os
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str = "sqlite:///ai_consultant.db"
    backup_dir: str = "backups"
    max_connections: int = 10

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    secret_key: str = "your-secret-key-change-in-production"
    allowed_hosts: List[str] = None
    debug: bool = False
    
    def __post_init__(self):
        if self.allowed_hosts is None:
            self.allowed_hosts = ["localhost", "127.0.0.1"]

@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "app.log"
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class AppConfig:
    """Main application configuration"""
    name: str = "AI Consultant Platform"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 5000
    database: DatabaseConfig = None
    security: SecurityConfig = None
    logging: LoggingConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.logging is None:
            self.logging = LoggingConfig()

class ConfigManager:
    """Configuration manager with environment variable support"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> AppConfig:
        """Load configuration from environment variables and defaults"""
        return AppConfig(
            debug=self._get_bool_env('DEBUG', False),
            host=self._get_env('HOST', '127.0.0.1'),
            port=self._get_int_env('PORT', 5000),
            database=DatabaseConfig(
                url=self._get_env('DATABASE_URL', 'sqlite:///ai_consultant.db'),
                backup_dir=self._get_env('BACKUP_DIR', 'backups'),
                max_connections=self._get_int_env('MAX_CONNECTIONS', 10)
            ),
            security=SecurityConfig(
                secret_key=self._get_env('SECRET_KEY', 'your-secret-key-change-in-production'),
                allowed_hosts=self._get_list_env('ALLOWED_HOSTS', ['localhost', '127.0.0.1']),
                debug=self._get_bool_env('DEBUG', False)
            ),
            logging=LoggingConfig(
                level=self._get_env('LOG_LEVEL', 'INFO'),
                format=self._get_env('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
                file=self._get_env('LOG_FILE', 'app.log'),
                max_size=self._get_int_env('LOG_MAX_SIZE', 10 * 1024 * 1024),
                backup_count=self._get_int_env('LOG_BACKUP_COUNT', 5)
            )
        )
    
    def _get_env(self, key: str, default: str) -> str:
        """Get environment variable with default"""
        return os.getenv(key, default)
    
    def _get_int_env(self, key: str, default: int) -> int:
        """Get integer environment variable with default"""
        value = os.getenv(key)
        return int(value) if value else default
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean environment variable with default"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def _get_list_env(self, key: str, default: List[str]) -> List[str]:
        """Get list environment variable with default"""
        value = os.getenv(key)
        return value.split(',') if value else default
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        if self.config.security.secret_key == 'your-secret-key-change-in-production':
            issues.append("WARNING: Using default secret key. Change SECRET_KEY in production.")
        
        if self.config.debug:
            issues.append("WARNING: Debug mode is enabled. Disable in production.")
        
        if not os.path.exists(self.config.database.backup_dir):
            try:
                os.makedirs(self.config.database.backup_dir)
            except Exception as e:
                issues.append(f"ERROR: Cannot create backup directory: {e}")
        
        return issues

# Global configuration instance
config_manager = ConfigManager()
config = config_manager.config

# Validate configuration on import
validation_issues = config_manager.validate()
if validation_issues:
    print("Configuration Issues:")
    for issue in validation_issues:
        print(f"  {issue}")
