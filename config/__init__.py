"""
Configuration module for Resource Monitor Server
"""

from .config import config, Config
from .config import (
    get_database_url,
    get_server_config,
    get_app_config,
    get_cors_config
)

__all__ = [
    'config',
    'Config',
    'get_database_url',
    'get_server_config',
    'get_app_config',
    'get_cors_config'
] 