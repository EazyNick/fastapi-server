"""
데이터베이스 연결 테스트 스크립트
MySQL 서버 연결, 데이터베이스 존재 여부, 테이블 생성 등을 테스트합니다.
"""

import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import pymysql

from config.config import config
from model import Base, Host, Container
from logger import logger

def test_basic_mysql_connection():
    """기본 MySQL 서버 연결 테스트"""
    logger.info("="*60)
    logger.info("1. 기본 MySQL 서버 연결 테스트")
    logger.info("="*60)
    
    try:
        # PyMySQL로 직접 연결 테스트
        connection = pymysql.connect(
            host=config.get_mysql_host(),
            port=config.get_mysql_port(),
            user=config.get_mysql_user(),
            password=config.get_mysql_password(),
            charset=config.get_mysql_charset()
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logger.info(f"✅ MySQL 서버 연결 성공!")
            logger.info(f"   MySQL 버전: {version[0]}")
            
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ MySQL 서버 연결 실패: {str(e)}")
        return False

def test_database_exists():
    """데이터베이스 존재 여부 테스트"""
    logger.info("="*60)
    logger.info("2. 데이터베이스 존재 여부 테스트")
    logger.info("="*60)
    
    try:
        connection = pymysql.connect(
            host=config.get_mysql_host(),
            port=config.get_mysql_port(),
            user=config.get_mysql_user(),
            password=config.get_mysql_password(),
            charset=config.get_mysql_charset()
        )
        
        with connection.cursor() as cursor:
            # 모든 데이터베이스 조회
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            logger.info(f"   사용 가능한 데이터베이스: {databases}")
            
            target_db = config.get_mysql_database()
            if target_db in databases:
                logger.info(f"✅ 데이터베이스 '{target_db}' 존재함")
                result = True
            else:
                logger.warning(f"⚠️  데이터베이스 '{target_db}' 존재하지 않음")
                
                # 데이터베이스 생성 시도
                try:
                    cursor.execute(f"CREATE DATABASE {target_db}")
                    logger.info(f"✅ 데이터베이스 '{target_db}' 생성 완료")
                    result = True
                except Exception as create_error:
                    logger.error(f"❌ 데이터베이스 생성 실패: {str(create_error)}")
                    result = False
                    
        connection.close()
        return result
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 확인 실패: {str(e)}")
        return False

def test_sqlalchemy_connection():
    """SQLAlchemy 엔진 연결 테스트"""
    logger.info("="*60)
    logger.info("3. SQLAlchemy 엔진 연결 테스트")
    logger.info("="*60)
    
    try:
        DATABASE_URL = config.get_database_url()
        logger.info(f"   데이터베이스 URL: {DATABASE_URL.replace(config.get_mysql_password(), '***')}")
        
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_size=5,
            max_overflow=10
        )
        
        # 연결 테스트
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info(f"✅ SQLAlchemy 엔진 연결 성공!")
            logger.info(f"   테스트 쿼리 결과: {result.fetchone()}")
            
        engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"❌ SQLAlchemy 엔진 연결 실패: {str(e)}")
        return False



def test_table_creation():
    """테이블 생성 테스트"""
    logger.info("="*60)
    logger.info("4. 테이블 생성 테스트")
    logger.info("="*60)
    
    try:
        DATABASE_URL = config.get_database_url()
        engine = create_engine(DATABASE_URL, echo=False)
        
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 테이블 생성 성공!")
        
        # 생성된 테이블 확인
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"   생성된 테이블: {tables}")
            
        engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"❌ 테이블 생성 실패: {str(e)}")
        return False

def test_real_data_insert():
    """실제 데이터 형식으로 INSERT 테스트"""
    logger.info("="*60)
    logger.info("5. 실제 데이터 INSERT 테스트")
    logger.info("="*60)
    
    try:
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime
        
        DATABASE_URL = config.get_database_url()
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        # 실제 Host 데이터 INSERT
        logger.info("   1) 실제 Host 데이터 INSERT")
        real_host = Host(
            host_name="DESKTOP-ZINOPC",
            cpu_percentage=3.9,
            cpu_cores=16,
            cpu_threads=32,
            memory_usage=18.1,
            memory_percentage=57.9,
            get_datetime=datetime.strptime("2025-06-23 03:02:50", "%Y-%m-%d %H:%M:%S")
        )
        
        db.add(real_host)
        db.commit()
        db.refresh(real_host)
        logger.info(f"   ✅ Host 데이터 INSERT 성공: ID={real_host.id}, 호스트명={real_host.host_name}")
        
        # 실제 Container 데이터 INSERT
        logger.info("   2) 실제 Container 데이터 INSERT")
        real_container = Container(
            engine_type="docker",
            cluster_name="DESKTOP-ZINOPC",
            node_name="DESKTOP-ZINOPC",
            container_name="tomcat1",
            status="running",
            cpu_percentage=0.0,
            memory_usage=119.5,
            memory_percentage=0.8,
            get_datetime=datetime.strptime("2025-06-23 03:02:48", "%Y-%m-%d %H:%M:%S"),
            host_id=real_host.id
        )
        
        db.add(real_container)
        db.commit()
        logger.info(f"   ✅ Container 데이터 INSERT 성공: ID={real_container.id}, 컨테이너명={real_container.container_name}")
        
        # 관계 확인
        logger.info("   3) 관계 확인")
        host_with_containers = db.query(Host).filter(Host.id == real_host.id).first()
        if host_with_containers and host_with_containers.containers:
            logger.info(f"   ✅ Host-Container 관계 확인 성공: {len(host_with_containers.containers)}개 컨테이너")
        
        # 테스트 데이터 정리
        logger.info("   4) 테스트 데이터 정리")
        db.delete(real_container)
        db.delete(real_host)
        db.commit()
        logger.info("   ✅ 테스트 데이터 정리 완료")
        
        db.close()
        engine.dispose()
        
        logger.info("✅ 실제 데이터 INSERT 테스트 성공!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 실제 데이터 INSERT 테스트 실패: {str(e)}")
        return False

def test_crud_operations():
    """단계별 상세 CRUD 작업 테스트"""
    logger.info("="*60)
    logger.info("6. CRUD 작업 테스트")
    logger.info("="*60)
    
    try:
        from sqlalchemy.orm import sessionmaker
        
        DATABASE_URL = config.get_database_url()
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        # 1. 삽입 테스트
        logger.info("   1) 데이터 삽입 테스트")
        test_host = Host(
            host_name="test-host-detailed",
            cpu_percentage=15.5,
            cpu_cores=4,
            cpu_threads=8,
            memory_usage=1024.0,
            memory_percentage=30.0,
            get_datetime=datetime.now()
        )
        
        db.add(test_host)
        db.commit()
        logger.info("   ✅ 데이터 삽입 성공")
        
        # 2. 조회 테스트
        logger.info("   2) 데이터 조회 테스트")
        created_host = db.query(Host).filter(Host.host_name == "test-host-detailed").first()
        if created_host:
            logger.info(f"   ✅ 데이터 조회 성공: ID={created_host.id}, 호스트명={created_host.host_name}")
        else:
            logger.error("   ❌ 데이터 조회 실패")
            return False
            
        # 3. 수정 테스트
        logger.info("   3) 데이터 수정 테스트")
        original_cpu = created_host.cpu_percentage
        created_host.cpu_percentage = 20.0
        db.commit()
        
        updated_host = db.query(Host).filter(Host.id == created_host.id).first()
        if updated_host and updated_host.cpu_percentage == 20.0:
            logger.info(f"   ✅ 데이터 수정 성공: CPU 사용률 {original_cpu}% → {updated_host.cpu_percentage}%")
        else:
            logger.error("   ❌ 데이터 수정 실패")
            return False
            
        # 4. 삭제 테스트
        logger.info("   4) 데이터 삭제 테스트")
        host_id = created_host.id
        db.delete(created_host)
        db.commit()
        
        deleted_host = db.query(Host).filter(Host.id == host_id).first()
        if deleted_host is None:
            logger.info("   ✅ 데이터 삭제 성공")
        else:
            logger.error("   ❌ 데이터 삭제 실패")
            return False
            
        db.close()
        engine.dispose()
        
        logger.info("✅ 모든 단계별 CRUD 작업 성공!")
        return True
        
    except Exception as e:
        logger.error(f"❌ CRUD 작업 실패: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    logger.info("🚀 데이터베이스 연결 테스트 시작")
    logger.info(f"⏰ 테스트 시간: {datetime.now()}")
    logger.info("")
    
    tests = [
        ("기본 MySQL 연결", test_basic_mysql_connection),
        ("데이터베이스 존재 확인", test_database_exists),
        ("SQLAlchemy 연결", test_sqlalchemy_connection),
        ("테이블 생성", test_table_creation),
        ("실제 데이터 INSERT", test_real_data_insert),
        ("CRUD 작업", test_crud_operations),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} 테스트 중 예외 발생: {str(e)}")
            results.append((test_name, False))
        
        logger.info("")  # 빈 줄 추가
    
    # 결과 요약
    logger.info("="*60)
    logger.info("📊 테스트 결과 요약")
    logger.info("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("")
    logger.info(f"📈 총 테스트: {len(results)}개")
    logger.info(f"✅ 성공: {passed}개")
    logger.info(f"❌ 실패: {failed}개")
    
    if failed == 0:
        logger.info("🎉 모든 테스트가 성공했습니다! 데이터베이스 연결이 정상입니다.")
        return True
    else:
        logger.warning(f"⚠️  {failed}개의 테스트가 실패했습니다. 설정을 확인해주세요.")
        return False

if __name__ == "__main__":
    try:
        # 동기 실행
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"테스트 실행 중 오류 발생: {str(e)}")
        sys.exit(1) 