import os
import shutil
import subprocess
import gzip
import json
from datetime import datetime
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)

CONFIG_PATH = Path("config/optimizer_settings.json")
CUSTOM_BACKUP_DIR = Path("custom_backups")
BACKUP_ROOT = Path("backups")
TIMESHIFT_CMD = shutil.which("timeshift") or "timeshift"

# 사용자 정의 백업 대상 로드
def load_custom_paths():
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
            return config.get("restore_settings", {}).get("custom_backup", {}).get("paths", [])
    except Exception as e:
        logger.error(f"[설정 로드 실패] 사용자 정의 경로 로딩 실패: {e}")
        return []

def compress_file(src_path, dest_path):
    if os.path.isdir(src_path):
        shutil.make_archive(dest_path, 'gztar', src_path)
    else:
        with open(src_path, 'rb') as f_in:
            with gzip.open(dest_path.with_suffix(dest_path.suffix + ".gz"), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

# 사용자 정의 백업 생성
def custom_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = CUSTOM_BACKUP_DIR / timestamp
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

# 사용자 정의 백업 목록 확인
def list_custom_backups():
    if not CUSTOM_BACKUP_DIR.exists():
        return []
    return sorted(CUSTOM_BACKUP_DIR.iterdir(), key=os.path.getmtime, reverse=True)

# 사용자 정의 복원
def restore_custom_backup(file_path, restore_dest):
    try:
        if str(file_path).endswith(".tar.gz"):
            shutil.unpack_archive(file_path, restore_dest)
        else:
            with gzip.open(file_path, 'rb') as f_in, open(os.path.join(restore_dest, Path(file_path).stem), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return True
    except Exception as e:
        logger.error(f"[복원 실패] {file_path} -> {restore_dest} | 오류: {e}")
        return False

# 사용자 정의 삭제
def delete_custom_backup(file_path):
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        logger.error(f"[삭제 실패] {file_path} | 오류: {e}")
        return False

# Timeshift 스냅샷 생성
def create_timeshift_snapshot():
    if shutil.which("timeshift") is None:
        logger.error("❌ Timeshift가 설치되어 있지 않습니다.")
        return False
    try:
        result = subprocess.run(["sudo", TIMESHIFT_CMD, "--create", "--comments", "Snapshot by Linux Optimizer GUI"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Timeshift 스냅샷 생성 성공")
            return True
        else:
            logger.error(f"❌ Timeshift 스냅샷 생성 실패: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Timeshift 실행 오류: {e}")
        return False

# Timeshift 스냅샷 목록
def list_timeshift_snapshots():
    if shutil.which("timeshift") is None:
        logger.error("❌ Timeshift가 설치되어 있지 않습니다.")
        return "Timeshift가 설치되어 있지 않습니다."
    try:
        result = subprocess.run(["sudo", TIMESHIFT_CMD, "--list"], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        logger.error(f"❌ Timeshift 스냅샷 목록 조회 실패: {e}")
        return ""

# 복원, 삭제는 CLI 안내 메시지만
def restore_timeshift():
    return "🔧 Timeshift 복원은 CLI에서 수동 복원 권장 (timeshift --restore)"

def delete_timeshift():
    return "🔧 Timeshift 스냅샷 삭제는 CLI에서 수동 삭제 권장 (timeshift --delete)"
