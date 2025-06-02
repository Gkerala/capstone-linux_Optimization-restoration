import os
import shutil
from datetime import datetime
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 복원 대상 경로들
RESTORE_TARGETS = {
    "sshd_config": "/etc/ssh/sshd_config",
    "sysctl.conf": "/etc/sysctl.conf",
    "crontab": "/var/spool/cron/crontabs/root",
    "optimizer_config": "config/optimizer_settings.json"
}

BACKUP_ROOT = Path("backups")

def create_backup():
    """현재 설정 상태를 백업"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_ROOT / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)

    for name, path in RESTORE_TARGETS.items():
        try:
            dest = backup_path / name
            if os.path.exists(path):
                shutil.copy2(path, dest)
                logger.info(f"[백업 완료] {path} -> {dest}")
            else:
                logger.warning(f"[누락] 대상 파일 존재하지 않음: {path}")
        except Exception as e:
            logger.error(f"[오류] {path} 백업 실패: {e}")

    logger.info(f"✅ 백업 완료: {backup_path}")
    return str(backup_path)


def list_restore_points():
    """복원 가능한 백업 목록 출력"""
    if not BACKUP_ROOT.exists():
        print("❌ 복원 포인트가 없습니다.")
        return []

    restore_points = sorted(BACKUP_ROOT.iterdir(), key=os.path.getmtime, reverse=True)
    for i, p in enumerate(restore_points, 1):
        print(f"{i}. {p.name}")
    return restore_points


def restore_backup(backup_dir):
    """지정된 백업 디렉토리로 복원"""
    backup_path = BACKUP_ROOT / backup_dir
    if not backup_path.exists():
        logger.error(f"❌ 복원 디렉토리 없음: {backup_path}")
        return

    for name, path in RESTORE_TARGETS.items():
        src = backup_path / name
        if src.exists():
            try:
                shutil.copy2(src, path)
                logger.info(f"[복원 성공] {src} -> {path}")
            except Exception as e:
                logger.error(f"[복원 실패] {src} -> {path} | 오류: {e}")
        else:
            logger.warning(f"[누락] 백업에 해당 파일 없음: {name}")

    logger.info(f"✅ 복원 완료: {backup_path}")


if __name__ == "__main__":
    print("🛠️ 복원 기능 테스트")
    print("1. 백업 생성\n2. 복원 목록 확인\n3. 복원 실행")
    choice = input("선택 (1~3): ").strip()

    if choice == "1":
        create_backup()
    elif choice == "2":
        list_restore_points()
    elif choice == "3":
        rp = input("복원할 디렉토리 이름 입력: ").strip()
        if rp:
            restore_backup(rp)
        else:
            print("❌ 복원 디렉토리 이름이 입력되지 않았습니다.")
    else:
        print("❌ 잘못된 선택")
