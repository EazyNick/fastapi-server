from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from model import Host, Container, SystemResourceData, HostResponse, ContainerResponse
from database import get_db, startup_db, shutdown_db
from config.config import config, get_app_config, get_cors_config
from utils import make_json_result, log_received_data, log_exception_with_traceback
from logger import logger
import traceback

# taskkill /PID 4364 /F
# uvicorn main:app --reload

# FastAPI 앱 생성
app_config = get_app_config()
app = FastAPI(
    title=app_config["title"],
    description=app_config["description"],
    version=app_config["version"],
    debug=app_config["debug"]
)

# CORS 설정
cors_config = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
)

# 데이터베이스 초기화 이벤트
@app.on_event("startup")
async def startup_event():
    await startup_db()
    logger.info("데이터베이스 연결 확인 및 테이블 초기화 완료")
    logger.info(f"데이터베이스: {config.get_mysql_database()} (per-request 연결 방식)")

@app.on_event("shutdown")
async def shutdown_event():
    await shutdown_db()
    logger.info("데이터베이스 엔진 리소스 정리 완료")

@app.get("/")
def read_root():
    return {
        "message": "Resource Monitor Server가 실행 중입니다.",
        "version": config.get_app_version(),
        "title": config.get_app_title()
    }

@app.get("/health")
def health_check():
    """서버 상태를 확인합니다."""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow(),
        "version": config.get_app_version()
    }

@app.get("/config")
def get_config():
    """현재 설정 정보를 반환합니다 (민감한 정보 제외)."""
    return {
        "app": {
            "title": config.get_app_title(),
            "description": config.get_app_description(),
            "version": config.get_app_version(),
            "debug": config.get_app_debug()
        },
        "server": {
            "host": config.get_server_host(),
            "port": config.get_server_port(),
            "log_level": config.get_server_log_level()
        },
        "database": {
            "echo": config.get_database_echo(),
            "pool_size": config.get_database_pool_size(),
            "max_overflow": config.get_database_max_overflow()
        },
        "mysql": {
            "host": config.get_mysql_host(),
            "port": config.get_mysql_port(),
            "user": config.get_mysql_user(),
            "database": config.get_mysql_database(),
            "charset": config.get_mysql_charset()
            # password는 보안상 제외
        },
        "cors": {
            "allow_origins": config.get_cors_allow_origins(),
            "allow_methods": config.get_cors_allow_methods(),
            "allow_credentials": config.get_cors_allow_credentials()
        },
        "logging": {
            "level": config.get_logging_level(),
            "file_path": config.get_logging_file_path()
        }
    }

# Agent로부터 자원 사용량 데이터를 받는 엔드포인트
@app.post("/api/resources", response_model=dict)
async def receive_resource_data(
    resource_data: SystemResourceData,
    db: Session = Depends(get_db)
):
    """
    Agent로부터 시스템 자원 사용량 데이터를 받아 데이터베이스에 저장합니다.
    """
    try:
        # 수신된 데이터 로깅
        log_received_data(resource_data.host, resource_data.containers, logger)
        
        # 호스트 정보 처리
        host_data = resource_data.host
        
        # 기존 호스트 확인
        existing_host = db.query(Host).filter(Host.host_name == host_data.host_name).first()
        
        if existing_host:
            # 기존 호스트 정보 업데이트
            existing_host.cpu_percentage = host_data.cpu_percentage
            existing_host.cpu_cores = host_data.cpu_cores
            existing_host.cpu_threads = host_data.cpu_threads
            existing_host.memory_usage = host_data.memory_usage
            existing_host.memory_percentage = host_data.memory_percentage
            existing_host.get_datetime = datetime.strptime(host_data.get_datetime, "%Y-%m-%d %H:%M:%S")
            host_record = existing_host
        else:
            # 새로운 호스트 생성
            host_record = Host(
                host_name=host_data.host_name,
                cpu_percentage=host_data.cpu_percentage,
                cpu_cores=host_data.cpu_cores,
                cpu_threads=host_data.cpu_threads,
                memory_usage=host_data.memory_usage,
                memory_percentage=host_data.memory_percentage,
                get_datetime=datetime.strptime(host_data.get_datetime, "%Y-%m-%d %H:%M:%S")
            )
            db.add(host_record)
        
        db.commit()
        db.refresh(host_record)
        
        # 컨테이너 정보 처리
        container_records = []
        for container_data in resource_data.containers:
            container_record = Container(
                engine_type=container_data.engine_type,
                cluster_name=container_data.cluster_name,
                node_name=container_data.node_name,
                container_name=container_data.container_name,
                status=container_data.status,
                cpu_percentage=container_data.cpu_percentage,
                memory_usage=container_data.memory_usage,
                memory_percentage=container_data.memory_percentage,
                get_datetime=datetime.strptime(container_data.get_datetime, "%Y-%m-%d %H:%M:%S"),
                host_id=host_record.id
            )
            db.add(container_record)
            container_records.append(container_record)
        
        db.commit()
        
        logger.info(f"호스트 '{host_data.host_name}'의 자원 사용량 데이터가 성공적으로 저장되었습니다. 컨테이너 수: {len(container_records)}")
        
        return {
            "status": "success",
            "message": "자원 사용량 데이터가 성공적으로 저장되었습니다.",
            "host_id": host_record.id,
            "containers_count": len(container_records),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        db.rollback()
        log_exception_with_traceback(e, logger, "데이터 저장 중 오류 발생")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 저장 중 오류가 발생했습니다: {str(e)}"
        )

# 호스트 목록 조회
@app.get("/api/hosts", response_model=List[HostResponse])
async def get_hosts(db: Session = Depends(get_db)):
    """
    등록된 모든 호스트 정보를 조회합니다.
    """
    hosts = db.query(Host).all()
    return hosts

# 특정 호스트의 컨테이너 조회
@app.get("/api/hosts/{host_id}/containers", response_model=List[ContainerResponse])
async def get_host_containers(host_id: int, db: Session = Depends(get_db)):
    """
    특정 호스트의 모든 컨테이너 정보를 조회합니다.
    """
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"호스트 ID {host_id}를 찾을 수 없습니다."
        )
    
    containers = db.query(Container).filter(Container.host_id == host_id).all()
    return containers

# 모든 컨테이너 조회
@app.get("/api/containers", response_model=List[ContainerResponse])
async def get_all_containers(db: Session = Depends(get_db)):
    """
    모든 컨테이너 정보를 조회합니다.
    """
    containers = db.query(Container).all()
    return containers



if __name__ == "__main__":
    import uvicorn
    server_config = {
        "host": config.get_server_host(),
        "port": config.get_server_port(),
        "reload": config.get_server_reload(),
        "log_level": config.get_server_log_level()
    }
    logger.info(f"서버 시작: {server_config}")
    uvicorn.run(app, **server_config)