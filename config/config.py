import configparser
import os
from typing import Optional, List
from pathlib import Path

class Config:
    def __init__(self, config_file: str = "config/config.ini"):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """설정 파일을 로드합니다."""
        config_path = Path(self.config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {self.config_file}")
        
        self.config.read(self.config_file, encoding='utf-8')
    
    def _get_env_or_config(self, section: str, key: str, default: Optional[str] = None) -> Optional[str]:
        """환경변수를 우선으로 하고, 없으면 설정 파일에서 가져옵니다."""
        env_key = f"{section.upper()}_{key.upper()}"
        env_value = os.getenv(env_key)
        
        if env_value is not None:
            return env_value
        
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def _get_bool(self, section: str, key: str, default: bool = False) -> bool:
        """Boolean 값을 가져옵니다."""
        value = self._get_env_or_config(section, key, str(default))
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def _get_int(self, section: str, key: str, default: int = 0) -> int:
        """Integer 값을 가져옵니다."""
        value = self._get_env_or_config(section, key, str(default))
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def _get_float(self, section: str, key: str, default: float = 0.0) -> float:
        """Float 값을 가져옵니다."""
        value = self._get_env_or_config(section, key, str(default))
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _get_list(self, section: str, key: str, default: List[str] = None) -> List[str]:
        """콤마로 구분된 리스트 값을 가져옵니다."""
        if default is None:
            default = []
        
        value = self._get_env_or_config(section, key, ",".join(default))
        if not value:
            return default
        
        return [item.strip() for item in value.split(",")]
    
    # MySQL 설정
    def get_mysql_host(self) -> str:
        return self._get_env_or_config("mysql", "host", "localhost")
    
    def get_mysql_port(self) -> int:
        return self._get_int("mysql", "port", 3306)
    
    def get_mysql_user(self) -> str:
        return self._get_env_or_config("mysql", "user", "root")
    
    def get_mysql_password(self) -> str:
        # 환경변수 MYSQL_PASSWORD에서 우선 가져오기
        password = os.getenv("MYSQL_PASSWORD")
        if password:
            return password
        
        # 환경변수가 없으면 설정 파일에서 가져오기 (보안상 권장하지 않음)
        return self._get_env_or_config("mysql", "password", "")
    
    def get_mysql_database(self) -> str:
        return self._get_env_or_config("mysql", "database", "test")
    
    def get_mysql_charset(self) -> str:
        return self._get_env_or_config("mysql", "charset", "utf8mb4")
    
    # Database 설정
    def get_database_url(self) -> str:
        """MySQL 설정을 조합하여 DATABASE_URL을 생성합니다."""
        # 직접 DATABASE_URL이 환경변수로 설정된 경우 우선 사용
        direct_url = os.getenv("DATABASE_URL")
        if direct_url:
            return direct_url
        
        # MySQL 설정으로 URL 생성
        host = self.get_mysql_host()
        port = self.get_mysql_port()
        user = self.get_mysql_user()
        password = self.get_mysql_password()
        database = self.get_mysql_database()
        charset = self.get_mysql_charset()
        
        if not password:
            raise ValueError("MySQL 비밀번호가 설정되지 않았습니다. 환경변수 MYSQL_PASSWORD를 설정해주세요.")
        
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"
    
    def get_database_echo(self) -> bool:
        return self._get_bool("database", "echo", False)
    
    def get_database_pool_size(self) -> int:
        return self._get_int("database", "pool_size", 0)
    
    def get_database_max_overflow(self) -> int:
        return self._get_int("database", "max_overflow", 0)
    
    def get_database_pool_pre_ping(self) -> bool:
        return self._get_bool("database", "pool_pre_ping", True)
    
    def get_database_pool_recycle(self) -> int:
        return self._get_int("database", "pool_recycle", 3600)
    
    # Server 설정
    def get_server_host(self) -> str:
        return self._get_env_or_config("server", "host", "0.0.0.0")
    
    def get_server_port(self) -> int:
        return self._get_int("server", "port", 8000)
    
    def get_server_reload(self) -> bool:
        return self._get_bool("server", "reload", True)
    
    def get_server_log_level(self) -> str:
        return self._get_env_or_config("server", "log_level", "info")
    
    # App 설정
    def get_app_title(self) -> str:
        return self._get_env_or_config("app", "title", "Resource Monitor Server")
    
    def get_app_description(self) -> str:
        return self._get_env_or_config("app", "description", "Agent로부터 Docker 자원 사용량 정보를 수집하는 서버")
    
    def get_app_version(self) -> str:
        return self._get_env_or_config("app", "version", "1.0.0")
    
    def get_app_debug(self) -> bool:
        return self._get_bool("app", "debug", False)
    
    # CORS 설정
    def get_cors_allow_origins(self) -> List[str]:
        return self._get_list("cors", "allow_origins", ["*"])
    
    def get_cors_allow_methods(self) -> List[str]:
        return self._get_list("cors", "allow_methods", ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    def get_cors_allow_headers(self) -> List[str]:
        return self._get_list("cors", "allow_headers", ["*"])
    
    def get_cors_allow_credentials(self) -> bool:
        return self._get_bool("cors", "allow_credentials", True)
    
    # Logging 설정
    def get_logging_level(self) -> str:
        return self._get_env_or_config("logging", "level", "INFO")
    
    def get_logging_format(self) -> str:
        return self._get_env_or_config("logging", "format", 
                                     "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    def get_logging_file_path(self) -> str:
        return self._get_env_or_config("logging", "file_path", "logs/app.log")
    
    def get_logging_max_file_size(self) -> int:
        return self._get_int("logging", "max_file_size", 10485760)  # 10MB
    
    def get_logging_backup_count(self) -> int:
        return self._get_int("logging", "backup_count", 5)
    
    # Security 설정
    def get_security_secret_key(self) -> str:
        return self._get_env_or_config("security", "secret_key", "your-secret-key-here")
    
    def get_security_algorithm(self) -> str:
        return self._get_env_or_config("security", "algorithm", "HS256")
    
    def get_security_access_token_expire_minutes(self) -> int:
        return self._get_int("security", "access_token_expire_minutes", 30)
    
    # Monitoring 설정
    def get_monitoring_max_records_per_host(self) -> int:
        return self._get_int("monitoring", "max_records_per_host", 1000)
    
    def get_monitoring_cleanup_interval_hours(self) -> int:
        return self._get_int("monitoring", "cleanup_interval_hours", 24)
    
    def get_monitoring_data_retention_days(self) -> int:
        return self._get_int("monitoring", "data_retention_days", 30)

# 전역 설정 인스턴스
config = Config()

# 편의 함수들
def get_database_url() -> str:
    return config.get_database_url()

def get_server_config() -> dict:
    return {
        "host": config.get_server_host(),
        "port": config.get_server_port(),
        "reload": config.get_server_reload(),
        "log_level": config.get_server_log_level()
    }

def get_app_config() -> dict:
    return {
        "title": config.get_app_title(),
        "description": config.get_app_description(),
        "version": config.get_app_version(),
        "debug": config.get_app_debug()
    }

def get_cors_config() -> dict:
    return {
        "allow_origins": config.get_cors_allow_origins(),
        "allow_methods": config.get_cors_allow_methods(),
        "allow_headers": config.get_cors_allow_headers(),
        "allow_credentials": config.get_cors_allow_credentials()
    } 