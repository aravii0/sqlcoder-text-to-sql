"""
Configuration settings for SQLCoder Text-to-SQL application
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database settings
DATABASE_URL = f"sqlite:///{BASE_DIR}/database/sample_database.db"
DATABASE_ECHO = False  # Set to True for SQL query logging

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True
API_LOG_LEVEL = "info"

# Frontend settings
FRONTEND_HOST = "localhost"
FRONTEND_PORT = 8501

# SQLCoder settings
SQLCODER_MODEL = "defog/sqlcoder-7b-2"  # or "defog/sqlcoder-34b" for larger model
SQLCODER_DEVICE = "auto"  # "auto", "cpu", or "cuda"
SQLCODER_MAX_TOKENS = 2048
SQLCODER_TEMPERATURE = 0.1

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Security settings (for production)
SECRET_KEY = "your-secret-key-change-in-production"
ALLOW_ORIGINS = ["*"]  # Restrict in production

# Feature flags
ENABLE_QUERY_CACHING = True
ENABLE_QUERY_LOGGING = True
MAX_QUERY_RESULTS = 1000

class Settings:
    """Application settings class"""

    def __init__(self):
        self.database_url = DATABASE_URL
        self.api_host = API_HOST
        self.api_port = API_PORT
        self.frontend_port = FRONTEND_PORT
        self.sqlcoder_model = SQLCODER_MODEL
        self.log_level = LOG_LEVEL

    def get_database_path(self):
        """Get the absolute path to the database file"""
        return str(BASE_DIR / "database" / "sample_database.db")

    def is_database_exists(self):
        """Check if the database file exists"""
        return Path(self.get_database_path()).exists()

# Global settings instance
settings = Settings()
