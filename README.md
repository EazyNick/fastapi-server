# Resource Monitor Server

여러 Agent로부터 Docker 자원 사용량 정보를 수집하여 데이터베이스에 저장하는 FastAPI 서버 애플리케이션입니다.

## 기능

- Agent로부터 RESTful API를 통해 시스템 자원 사용량 데이터를 수집
- 호스트 및 컨테이너 정보를 MySQL 데이터베이스에 저장
- JSON 형식으로 데이터 송수신
- 실시간 모니터링 및 데이터 조회 API 제공
- 설정 파일을 통한 유연한 구성 관리
- 환경변수를 통한 설정 오버라이드 지원
- 로그 파일 로테이션 및 레벨 설정
- CORS 설정 지원
- 표준화된 JSON 응답 형식 지원 (success, resultCode, resultMessage, data)
- 상세한 로깅 및 예외 처리 (traceback 포함)
- 기존 코드와의 호환성 엔드포인트 제공
- 모듈화된 프로젝트 구조 (config, model, database, utils, logger 패키지 분리)

## 시스템 요구사항

- Python 3.8+
- FastAPI 0.116.0+
- SQLAlchemy 2.0+
- MySQL 8.0+ (AWS RDS)

## 설치 및 실행

1. 의존성 설치:

```bash
pip install -r requirements.txt
```

2. 설정 파일 생성:

```bash
# 설정 템플릿 파일을 복사
cp config/config.ini.example config/config.ini

# config/config.ini 파일을 열어서 MySQL 설정 부분을 실제 값으로 수정
# [mysql] 섹션에서 host, user, password, database 값을 변경
```

3. 서버 실행:

```bash
# 설정 파일 기본값으로 실행
python main.py

# 또는 uvicorn으로 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. 서버 확인:

- 브라우저에서 `http://localhost:8000` 접속
- API 문서: `http://localhost:8000/docs`
- 서버 상태: `http://localhost:8000/health`
- 현재 설정: `http://localhost:8000/config`

## 설정 관리

### 설정 파일 생성 (필수)

⚠️ **프로젝트 실행 전에 `config/config.ini` 파일을 생성해야 합니다.**

**간단한 방법:**

```bash
# 템플릿 파일을 복사하여 설정 파일 생성
cp config/config.ini.example config/config.ini

# 이후 config/config.ini 파일에서 MySQL 설정 부분을 실제 값으로 수정
```

**수동 생성 방법:**

`config/config.ini` 파일을 생성하고 아래 내용을 복사한 후, 실제 값으로 수정하세요:

```ini
[database]
echo = false
pool_size = 10
max_overflow = 20

[mysql]
host = your-mysql-host
port = 3306
user = your-mysql-user
password = your-mysql-password
database = your-database-name
charset = utf8mb4

[server]
host = 0.0.0.0
port = 8000
reload = true
log_level = info

[app]
title = Resource Monitor Server
description = Agent로부터 Docker 자원 사용량 정보를 수집하는 서버
version = 1.0.0
debug = false

[cors]
allow_origins = *
allow_methods = GET,POST,PUT,DELETE,OPTIONS
allow_headers = *
allow_credentials = true

[logging]
level = INFO
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
file_path = logs/app.log
max_file_size = 10485760
backup_count = 5
```

### 설정 값 수정 방법

위의 템플릿에서 다음 항목들을 실제 값으로 변경하세요:

- `host`: MySQL 서버 호스트 주소 (예: your-rds-host.amazonaws.com)
- `user`: MySQL 사용자명 (예: admin)
- `password`: MySQL 비밀번호 (예: your_secure_password)
- `database`: 사용할 데이터베이스 이름 (예: your_database)

### 환경변수 설정 (선택사항)

**MySQL 비밀번호 설정:**

MySQL 비밀번호는 다음 두 가지 방법 중 하나로 설정할 수 있습니다:

**방법 1: config.ini 파일에 직접 설정** (간단한 방법)

```ini
[mysql]
password = your_mysql_password
```

**방법 2: 환경변수로 설정** (보안상 더 권장)

```bash
export MYSQL_PASSWORD=your_mysql_password
```

환경변수가 설정되면 config.ini의 password보다 우선적으로 사용됩니다.

**선택적 환경변수:**

```bash
# MySQL 개별 설정 (config.ini 값을 오버라이드)
export MYSQL_HOST=your-mysql-host
export MYSQL_PORT=3306
export MYSQL_USER=your-mysql-user
export MYSQL_DATABASE=your-database-name
export MYSQL_CHARSET=utf8mb4

# 또는 직접 DATABASE_URL 설정 (위의 개별 설정보다 우선)
export DATABASE_URL="mysql+pymysql://user:password@host:port/database?charset=utf8mb4"

# 서버 설정
export SERVER_PORT=9000
export SERVER_HOST=0.0.0.0
export SERVER_RELOAD=false
export SERVER_LOG_LEVEL=info

# 애플리케이션 설정
export APP_DEBUG=true
export APP_TITLE="My Resource Monitor"

# 로깅 설정
export LOGGING_LEVEL=DEBUG
export LOGGING_FILE_PATH=logs/app.log

# 데이터베이스 연결 풀 설정
export DATABASE_ECHO=false
export DATABASE_POOL_SIZE=20
```

**환경변수 이름 규칙:**

- MySQL 비밀번호: `MYSQL_PASSWORD` (config.ini의 password보다 우선)
- 기타 설정: `{섹션}_{키}` 형태로 대문자 (예: `SERVER_PORT`, `APP_DEBUG`)

### 설정 섹션 설명

- **database**: 데이터베이스 연결 풀 설정
- **mysql**: MySQL 서버 연결 정보
- **server**: 서버 실행 설정
- **app**: 애플리케이션 기본 정보
- **cors**: CORS 정책 설정
- **logging**: 로그 설정
- **security**: 보안 설정 (JWT 등) - 현재 미사용
- **monitoring**: 모니터링 및 데이터 관리 설정 - 현재 미구현

## API 엔드포인트

### 1. 자원 사용량 데이터 수집

- **POST** `/api/resources`
- Agent로부터 호스트 및 컨테이너 자원 사용량 데이터를 받아 DB에 저장

### 2. 호스트 목록 조회

- **GET** `/api/hosts`
- 등록된 모든 호스트 정보 조회

### 3. 특정 호스트의 컨테이너 조회

- **GET** `/api/hosts/{host_id}/containers`
- 특정 호스트의 모든 컨테이너 정보 조회

### 4. 모든 컨테이너 조회

- **GET** `/api/containers`
- 모든 컨테이너 정보 조회

### 5. 서버 상태 확인

- **GET** `/health`
- 서버 상태 및 타임스탬프 확인

### 6. 설정 정보 조회

- **GET** `/config`
- 현재 서버 설정 정보 조회 (민감한 정보 제외)

### 7. 호환성 모니터링 데이터 수집

- **POST** `/monitor_info`
- 기존 코드와 호환되는 모니터링 데이터 수신 엔드포인트
- `node_name`을 `host_name`으로 자동 변환
- 표준화된 JSON 응답 형식 사용 (success, resultCode, resultMessage, data)

## 데이터 형식

Agent에서 서버로 전송하는 JSON 데이터 형식:

```json
{
  "host": {
    "host_name": "DESKTOP-ZINOPC",
    "cpu_percentage": 3.9,
    "cpu_cores": 16,
    "cpu_threads": 32,
    "memory_usage": 18.1,
    "memory_percentage": 57.9,
    "get_datetime": "2025-06-23 03:02:50"
  },
  "containers": [
    {
      "engine_type": "docker",
      "cluster_name": "DESKTOP-ZINOPC",
      "node_name": "DESKTOP-ZINOPC",
      "container_name": "tomcat3",
      "status": "exited",
      "cpu_percentage": 0,
      "memory_usage": 0,
      "memory_percentage": 0,
      "get_datetime": "2025-06-23 03:02:47"
    }
  ]
}
```

## 로깅

### 로그 설정

- 로그 레벨: `config/config.ini`의 `[logging]` 섹션에서 설정
- 로그 파일: `logs/app.log` (기본값)
- 로그 로테이션: 파일 크기 10MB, 백업 5개 파일 유지

### 로그 내용

- 서버 시작/종료 이벤트
- 데이터베이스 연결 상태
- 자원 사용량 데이터 저장 성공/실패
- API 요청 및 응답 정보
- 수신된 데이터 상세 정보 (호스트 및 컨테이너 정보)
- 오류 발생 시 상세 정보 및 traceback

## 새로운 기능들

### 1. 표준화된 JSON 응답 형식

모든 API 응답에서 일관된 형식을 제공합니다:

```json
{
  "success": true,
  "resultCode": "0",
  "resultMessage": "container_count: 2",
  "data": {
    "host_id": 1,
    "containers_count": 2,
    "timestamp": "2025-01-23T03:02:50"
  }
}
```

### 2. 상세한 로깅 및 예외 처리

- 수신된 데이터 상세 출력으로 디버깅 지원
- 예외 발생 시 전체 traceback 출력
- 구조화된 로그 형식으로 문제 진단 용이

## 데이터베이스 스키마

### hosts 테이블

- id (Primary Key)
- host_name (Unique)
- cpu_percentage
- cpu_cores
- cpu_threads
- memory_usage
- memory_percentage
- get_datetime

### containers 테이블

- id (Primary Key)
- engine_type
- cluster_name
- node_name
- container_name
- status
- cpu_percentage
- memory_usage
- memory_percentage
- get_datetime
- host_id (Foreign Key)

## 프로젝트 구조

```
fastapi-server/
├── config/
│   ├── __init__.py
│   ├── config.py          # 설정 관리 클래스
│   ├── config.ini         # 설정 파일 (사용자 생성 필요)
│   └── config.ini.example # 설정 파일 템플릿
├── model/
│   ├── __init__.py        # 모델 패키지 초기화
│   └── models.py          # 데이터베이스 및 API 모델
├── database/
│   ├── __init__.py        # 데이터베이스 패키지 초기화
│   └── database.py        # 데이터베이스 연결 관리
├── utils/
│   ├── __init__.py        # 유틸리티 패키지 초기화
│   └── utils.py           # 유틸리티 함수들
├── logs/
│   └── .gitkeep           # 로그 디렉토리
├── .gitignore             # Git 무시 파일 목록
├── main.py                # FastAPI 애플리케이션
├── logger.py              # 로깅 설정 관리
├── requirements.txt       # 의존성 패키지
└── README.md             # 프로젝트 설명
```

## 개발 환경

- **Framework**: FastAPI 0.116.0+
- **Database**: MySQL 8.0+ (AWS RDS)
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic 2.8+
- **Server**: Uvicorn 0.30+
- **Configuration**: ConfigParser (INI 파일)

## 환경별 설정

### 개발 환경

```bash
export APP_DEBUG=true
export LOGGING_LEVEL=DEBUG
export SERVER_RELOAD=true
```

### 프로덕션 환경

```bash
# 보안을 위해 환경변수로 비밀번호 설정 (권장)
export MYSQL_PASSWORD=your_secure_password

# 프로덕션 최적화 설정
export APP_DEBUG=false
export LOGGING_LEVEL=INFO
export SERVER_RELOAD=false
export DATABASE_ECHO=false
export DATABASE_POOL_SIZE=20
export DATABASE_MAX_OVERFLOW=30
```

## 보안 고려사항

### MySQL 비밀번호 설정 방법

- **개발 환경**: config.ini에 직접 설정 가능
- **프로덕션 환경**: 환경변수 `MYSQL_PASSWORD` 사용 권장

### 환경변수 설정 방법

```bash
# Linux/macOS
export MYSQL_PASSWORD=your_mysql_password

# Windows PowerShell
$env:MYSQL_PASSWORD="your_mysql_password"

# Windows CMD
set MYSQL_PASSWORD=your_mysql_password
```
