import logging
from pathlib import Path
import json

CONFIG_PATH = Path("config/optimizer_settings.json")

def get_logger(name=__name__):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # 이미 설정된 핸들러가 있다면 그대로 반환

    logger.setLevel(logging.DEBUG)

    # 기본 로그 경로
    default_log_path = Path("logs/system.log")

    # 설정 파일에서 로그 경로 로드
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
            log_path = Path(config.get("log_management", {}).get("log_file_path", default_log_path))
    except Exception:
        log_path = default_log_path

    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 파일 핸들러 추가
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 콘솔 출력도 유지하고 싶다면 StreamHandler도 추가
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
