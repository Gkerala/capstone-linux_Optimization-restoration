import os
import shutil
from datetime import datetime
from pathlib import Path
import json
import gzip
import subprocess
from src.utils.logger import get_logger

logger = get_logger(__name__)

CONFIG_PATH = Path("config/optimizer_settings.json")

# 설정 파일로부터 복원 대상 경로 로드
def load_restore_targets():
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
            return config.get("restore_settings", {}).get("restore_targets", {})
    except Exception as e:
        logger.error(f"[설정 로드 실패] restore_targets 로딩 실패: {e}")
        return {}

BACKUP_ROOT = Path("backups")
CUSTOM_ROOT = Path("custom_backups")


def compress_file(src_path, dest_path):
    with open(src_path, 'rb') as f_in:
        with gzip.open(dest_path.with_suffix(dest_path.suffix + ".gz"), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


# 기존 스냅샷 기능 (설정 파일을 압축하여 저장)
def create_snapshot():
    """현재 설정 상태를 백업 (스냅샷 생성 - 설정파일 기반)"""
    restore_targets = load_restore_targets()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_ROOT / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)

    for name, path in restore_targets.items():
        try:
            dest = backup_path / name
            if os.path.exists(path):
                compress_file(path, dest)
                logger.info(f"[백업 완료] {path} -> {dest}.gz")
            else:
                logger.warning(f"[누락] 대상 파일 존재하지 않음: {path}")
        except Exception as e:
            logger.error(f"[오류] {path} 백업 실패: {e}")

    logger.info(f"✅ 스냅샷 생성 완료: {backup_path}")
    return str(backup_path)


def list_snapshots():
    """복원 가능한 스냅샷 목록 출력 (설정파일 기반 스냅샷)"""
    if not BACKUP_ROOT.exists():
        print("❌ 스냅샷이 없습니다.")
        return []

    snapshots = sorted(BACKUP_ROOT.iterdir(), key=os.path.getmtime, reverse=True)
    for i, p in enumerate(snapshots, 1):
        print(f"{i}. {p.name}")
    return snapshots


def restore_snapshot(snapshot_name):
    """지정된 스냅샷으로 복원 (설정파일 기반)"""
    restore_targets = load_restore_targets()
    snapshot_path = BACKUP_ROOT / snapshot_name
    if not snapshot_path.exists():
        logger.error(f"❌ 복원 디렉토리 없음: {snapshot_path}")
        return

    for name, path in restore_targets.items():
        src = snapshot_path / f"{name}.gz"
        if src.exists():
            try:
                with gzip.open(src, 'rb') as f_in, open(path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                logger.info(f"[복원 성공] {src} -> {path}")
            except Exception as e:
                logger.error(f"[복원 실패] {src} -> {path} | 오류: {e}")
        else:
            logger.warning(f"[누락] 백업에 해당 파일 없음: {name}")

    logger.info(f"✅ 복원 완료: {snapshot_path}")


# 사용자 정의 백업 및 복원 기능 구현
def load_custom_paths():
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
            return config.get("restore_settings", {}).get("custom_backup", {}).get("paths", [])
    except Exception as e:
        logger.error(f"[설정 로드 실패] 사용자 정의 경로 로딩 실패: {e}")
        return []


def backup_custom():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = CUSTOM_ROOT / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)

    for path in load_custom_paths():
        try:
            name = Path(path).name
            dest = backup_path / name
            if os.path.exists(path):
                compress_file(path, dest)
                logger.info(f"[사용자 정의 백업] {path} -> {dest}.gz")
            else:
                logger.warning(f"[사용자 정의 백업 누락] 존재하지 않음: {path}")
        except Exception as e:
            logger.error(f"[사용자 정의 백업 실패] {path} | 오류: {e}")

    logger.info(f"✅ 사용자 정의 백업 완료: {backup_path}")
    return str(backup_path)


def list_custom_backups():
    if not CUSTOM_ROOT.exists():
        print("❌ 사용자 정의 백업 없음")
        return []

    entries = sorted(CUSTOM_ROOT.iterdir(), key=os.path.getmtime, reverse=True)
    for i, p in enumerate(entries, 1):
        print(f"{i}. {p.name}")
    return entries


# Timeshift 연동 기능 (시스템 전체 스냅샷)
def create_timeshift_snapshot():
    try:
        result = subprocess.run(["sudo", "timeshift", "--create", "--comments", "Snapshot by Linux Optimizer GUI"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Timeshift 스냅샷 생성 성공")
        else:
            logger.error(f"❌ Timeshift 스냅샷 생성 실패: {result.stderr}")
    except Exception as e:
        logger.error(f"❌ Timeshift 실행 오류: {e}")


def list_timeshift_snapshots():
    try:
        result = subprocess.run(["sudo", "timeshift", "--list"], capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
    except Exception as e:
        logger.error(f"❌ Timeshift 스냅샷 목록 조회 실패: {e}")
        return []


def restore_timeshift_snapshot():
    print("Timeshift 복원은 CLI에서 수동으로 진행하거나, 고급 GUI를 사용하세요.")


