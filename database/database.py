from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from model import Base
from config.config import config
from logger import logger

# 설정에서 데이터베이스 URL 가져오기
DATABASE_URL = config.get_database_url()

# SQLAlchemy 엔진 생성 (연결 풀 비활성화)
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=config.get_database_echo(),
    pool_size=config.get_database_pool_size(),
    max_overflow=config.get_database_max_overflow(),
    pool_pre_ping=config.get_database_pool_pre_ping(),
    pool_recycle=config.get_database_pool_recycle()
)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테이블 생성
def create_tables():
    try:
        logger.info("데이터베이스 테이블 확인 중...")
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 초기화 완료 (hosts, containers)")
    except Exception as e:
        logger.error(f"테이블 생성 중 오류 발생: {str(e)}")
        raise

# 데이터베이스 세션 dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 데이터베이스 초기화 (테이블 생성만)
async def startup_db():
    logger.info("데이터베이스 초기화 시작")
    try:
        create_tables()
        logger.info("데이터베이스 초기화 성공")
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {str(e)}")
        raise

# 데이터베이스 엔진 정리
async def shutdown_db():
    logger.info("데이터베이스 엔진 정리 시작")
    try:
        engine.dispose()
        logger.info("데이터베이스 엔진 정리 완료")
    except Exception as e:
        logger.error(f"데이터베이스 엔진 정리 중 오류: {str(e)}") 