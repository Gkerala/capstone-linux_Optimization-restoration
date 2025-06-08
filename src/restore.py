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
TIMESHIFT_CMD = "timeshift"


# 사용자 정의 백업 대상 로드
def load_custom_paths():
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
            return config.get("restore_settings", {}).get("custom_backup", {}).get("paths", [])
    except Exception as e:
        logger.error(f"[설정 로드 실패] 사용자 정의 경로 로딩 실패: {e}")
        return []


# 파일 압축
def compress_file(src_path, dest_path):
    with open(src_path, 'rb') as f_in, gzip.open(dest_path.with_suffix(dest_path.suffix + ".gz"), 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


# 사용자 정의 백업 생성
def custom_backup():
    from tkinter import filedialog
    file_path = filedialog.askopenfilename(title="📄 백업할 파일 선택")
    if not file_path:
        return "❌ 파일 선택이 취소됨."
    CUSTOM_BACKUP_DIR.mkdir(exist_ok=True)
    dest = CUSTOM_BACKUP_DIR / Path(file_path).name
    try:
        shutil.copy(file_path, dest)
        return f"✅ 파일 백업 완료: {dest}"
    except Exception as e:
        return f"❌ 백업 실패: {e}"


# 사용자 정의 백업 디렉토리 생성
def input_directory_and_backup():
    from tkinter import simpledialog
    dir_path = simpledialog.askstring("디렉토리 경로 입력", "📁 백업할 디렉토리 경로 입력 (예: /home/사용자/폴더명):")
    if not dir_path:
        return "❌ 입력 취소됨."
    if not Path(dir_path).is_dir():
        return f"❌ 유효하지 않은 디렉토리 경로: {dir_path}"

    CUSTOM_BACKUP_DIR.mkdir(exist_ok=True)
    archive_path = CUSTOM_BACKUP_DIR / (Path(dir_path).name + ".tar.gz")
    try:
        shutil.make_archive(str(archive_path).replace('.tar.gz', ''), 'gztar', dir_path)
        return f"✅ 디렉토리 백업 완료: {archive_path}"
    except Exception as e:
        return f"❌ 백업 실패: {e}"


# 사용자 정의 백업 목록 확인
def list_custom_backups():
    if not CUSTOM_BACKUP_DIR.exists():
        return []
    return sorted(CUSTOM_BACKUP_DIR.iterdir(), key=os.path.getmtime, reverse=True)


# 사용자 정의 복원
def restore_custom_backup(file_path: Path, restore_dest: str) -> bool:
    try:
        if file_path.suffix == ".gz":
            with gzip.open(file_path, 'rb') as f_in, open(os.path.join(restore_dest, file_path.stem), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        elif file_path.suffix.endswith(".tar.gz") or file_path.name.endswith(".tar.gz"):
            shutil.unpack_archive(str(file_path), extract_dir=restore_dest)
        else:
            shutil.copy(str(file_path), restore_dest)
        return True
    except Exception as e:
        logger.error(f"[복원 실패] {file_path} -> {restore_dest} | 오류: {e}")
        return False


# 사용자 정의 삭제
def delete_custom_backup(file_path: Path) -> bool:
    try:
        file_path.unlink()
        return True
    except Exception as e:
        logger.error(f"[삭제 실패] {file_path} | 오류: {e}")
        return False


# Timeshift 스냅샷 생성
def create_timeshift_snapshot():
    try:
        result = subprocess.run(["sudo", TIMESHIFT_CMD, "--create", "--comments", "Snapshot by Linux Optimizer GUI"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            return "✅ Timeshift 스냅샷 생성 완료"
        else:
            return f"❌ Timeshift 실패: {result.stderr}"
    except Exception as e:
        return f"❌ Timeshift 오류: {e}"


# Timeshift 목록
def list_timeshift_snapshots():
    try:
        result = subprocess.run(["sudo", TIMESHIFT_CMD, "--list"], capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"❌ Timeshift 목록 오류: {e}"


# 복원/삭제 (CLI 안내)
def restore_timeshift():
    return "🔧 Timeshift 복원은 CLI에서 권장 (sudo timeshift --restore)"


def delete_timeshift():
    return "🔧 Timeshift 삭제는 CLI에서 권장 (sudo timeshift --delete)"
