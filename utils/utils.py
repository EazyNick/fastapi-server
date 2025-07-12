from collections import OrderedDict
from typing import Any, Optional
import traceback
import logging
from logger import get_logger

logger = get_logger(__name__)

def make_json_result(is_success: bool, result_code: str, result_message: str, data: Optional[Any] = None) -> OrderedDict:
    """
    표준화된 JSON 응답 형식을 생성합니다.
    
    Args:
        is_success: 성공 여부
        result_code: 결과 코드
        result_message: 결과 메시지
        data: 응답 데이터 (선택사항)
        
    Returns:
        OrderedDict: 표준화된 응답 형식
    """
    json_data = OrderedDict()
    json_data['success'] = is_success
    json_data['resultCode'] = result_code
    json_data['resultMessage'] = result_message
    json_data['data'] = data
    return json_data

def log_received_data(host_data: Any, containers_data: Any, logger: logging.Logger) -> None:
    """
    수신된 데이터를 로그에 출력합니다.
    
    Args:
        host_data: 호스트 정보
        containers_data: 컨테이너 정보 리스트
        logger: 로거 인스턴스
    """
    logger.info("=" * 50)
    logger.info("수신된 데이터:")
    logger.info(f"호스트 정보: {host_data}")
    logger.info(f"컨테이너 정보 (총 {len(containers_data)}개): {containers_data}")
    logger.info("=" * 50)

def log_exception_with_traceback(exception: Exception, logger: logging.Logger, context: str = "") -> None:
    """
    예외 발생 시 상세한 traceback을 포함하여 로그를 출력합니다.
    
    Args:
        exception: 발생한 예외
        logger: 로거 인스턴스
        context: 예외 발생 컨텍스트
    """
    error_msg = f"[ERROR] {context}: {str(exception)}"
    logger.error(error_msg)
    logger.error("상세 오류 정보:")
    logger.error(traceback.format_exc()) 