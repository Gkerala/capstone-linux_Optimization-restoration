import os
import json
import pytest
from src.utils.config import ConfigLoader

CONFIG_FILE = "tests/test_settings.json"
SCHEMA_FILE = "tests/test_schema.json"

@pytest.fixture(scope="module", autouse=True)
def create_test_files():
    """테스트용 설정 파일과 스키마 파일을 생성하고 테스트 후 삭제"""
    # 테스트용 설정
    test_config = {
        "log_level": "INFO",
        "max_threads": 4
    }

    # 테스트용 스키마
    test_schema = {
        "type": "object",
        "properties": {
            "log_level": {
                "type": "string",
                "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]
            },
            "max_threads": {
                "type": "integer",
                "minimum": 1
            }
        },
        "required": ["log_level", "max_threads"]
    }

    # 파일 생성
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(test_config, f, indent=4)

    with open(SCHEMA_FILE, "w", encoding="utf-8") as f:
        json.dump(test_schema, f, indent=4)

    yield  # 테스트 실행

    # 테스트 후 정리
    os.remove(CONFIG_FILE)
    os.remove(SCHEMA_FILE)


def test_config_loads():
    """설정 파일을 정상적으로 불러오는지 테스트"""
    config = ConfigLoader(config_path=CONFIG_FILE, schema_path=SCHEMA_FILE)
    config.load_config()
    data = config.get_config()
    assert data["log_level"] == "INFO"
    assert data["max_threads"] == 4


def test_get_and_update():
    """설정 값을 불러오고 수정한 뒤 복원하는 테스트"""
    config = ConfigLoader(config_path=CONFIG_FILE, schema_path=SCHEMA_FILE)
    config.load_config()
    original = config.get_config()

    new_config = {
        "log_level": "DEBUG",
        "max_threads": 8
    }
    config.save_config(new_config)

    updated = config.get_config()
    assert updated["log_level"] == "DEBUG"
    assert updated["max_threads"] == 8

    # 원상 복구
    config.save_config(original)


def test_validate_config():
    """설정값이 스키마 기준으로 유효한지 확인"""
    config = ConfigLoader(config_path=CONFIG_FILE, schema_path=SCHEMA_FILE)
    config.load_config()
    config.load_schema()
    config.validate()


def test_invalid_update():
    """타입이 안 맞거나 enum에 없는 값은 반영되지 않아야 함"""
    config = ConfigLoader(config_path=CONFIG_FILE, schema_path=SCHEMA_FILE)
    config.load_schema()
    invalid_config = {
        "log_level": "INVALID",   # enum에 없음
        "max_threads": "eight"    # 문자열로 잘못됨
    }

    with pytest.raises(Exception):
        config.save_config(invalid_config)

