"""
Logger 설정 모듈 - 애플리케이션 전체의 로깅 설정을 관리합니다.
"""

import logging
import logging.handlers
from pathlib import Path
from config.config import config

def setup_logging():
    """
    애플리케이션의 로깅 설정을 초기화합니다.
    
    설정 파일(config.ini)에서 로깅 관련 설정을 읽어와서
    콘솔 출력과 파일 로그 로테이션을 설정합니다.
    """
    log_level = getattr(logging, config.get_logging_level().upper())
    log_format = config.get_logging_format()
    log_file_path = config.get_logging_file_path()
    
    # 로그 디렉토리 생성
    log_dir = Path(log_file_path).parent
    log_dir.mkdir(exist_ok=True)
    
    # 루트 로거 설정
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # 콘솔 출력
            logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=config.get_logging_max_file_size(),
                backupCount=config.get_logging_backup_count(),
                encoding='utf-8'
            )
        ]
    )

def get_logger(name: str = __name__) -> logging.Logger:
    """
    지정된 이름으로 로거 인스턴스를 반환합니다.
    
    Args:
        name: 로거 이름 (일반적으로 __name__ 사용)
        
    Returns:
        logging.Logger: 로거 인스턴스
    """
    return logging.getLogger(name)

# 로깅 설정 초기화
setup_logging()

# 기본 로거 인스턴스
logger = get_logger(__name__) 