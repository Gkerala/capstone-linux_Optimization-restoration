import os
import subprocess
import time
import re
import psutil
from src.utils.logger import get_logger
from src.utils.config import ConfigLoader
from src.utils.system import is_virtual_machine

logger = get_logger(__name__)

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        logger.info(f"[PASS] {command}")
    except subprocess.CalledProcessError as e:
        logger.error(f"[FAIL] {command} | 오류: {e}")

# 1. CPU 최적화
def optimize_cpu(cpu_config):
    section = "CPU"
    try:
        if is_virtual_machine():
            logger.warning(f"[SKIP] {section} | 가상 환경에서는 governor 설정 생략")
        else:
            if cpu_config.get("governor"):
                run_command(f"cpupower frequency-set -g {cpu_config['governor']}")

        for proc in cpu_config.get("priority_processes", []):
            run_command(f"renice -n -5 -p $(pgrep {proc} | head -n 1)")

        if cpu_config.get("enable_scheduler_tuning"):
            scheduler_policy = cpu_config.get("scheduler_policy", "SCHED_OTHER")
            policy_map = {
                "SCHED_FIFO": "-f", "SCHED_RR": "-r", "SCHED_BATCH": "-b",
                "SCHED_IDLE": "-i", "SCHED_OTHER": ""
            }
            option = policy_map.get(scheduler_policy.upper(), None)

            if option is None:
                logger.warning(f"[SKIP] {section} | 알 수 없는 scheduler_policy: {scheduler_policy}")
                return

            for proc in cpu_config.get("target_processes", []):
                run_command(f"chrt {option} -p 50 $(pgrep {proc} | head -n 1)")
        logger.info(f"[PASS] {section}")
    except Exception as e:
        logger.error(f"[FAIL] {section} | 오류: {e}")

# 2. IO 최적화
def optimize_io(io_config):
    section = "I/O"
    try:
        if is_virtual_machine():
            logger.warning(f"[SKIP] {section} | 가상환경에서 건너뜀")
            return

        if io_config.get("enable"):
            run_command(f"echo {io_config.get('scheduler', 'deadline')} | tee /sys/block/sda/queue/scheduler")
            run_command(f"blockdev --setra {io_config.get('read_ahead_kb', 128)} /dev/sda")
        logger.info(f"[PASS] {section}")
    except Exception as e:
        logger.error(f"[FAIL] {section} | 오류: {e}")

# 3. 메모리 최적화
def optimize_memory(mem_config):
    section = "Memory"
    try:
        run_command(f"sysctl vm.swappiness={mem_config['swappiness']}")

        if mem_config.get("drop_caches_on_schedule"):
            run_command(f"sync; echo {mem_config['drop_cache_mode']} > /proc/sys/vm/drop_caches")

        if "low_memory_threshold_percent" in mem_config:
            with open('/proc/meminfo') as f:
                meminfo = f.read()
            mem_total = int(re.search(r'MemTotal:\s+(\d+)', meminfo).group(1))
            mem_available = int(re.search(r'MemAvailable:\s+(\d+)', meminfo).group(1))
            available_percent = (mem_available / mem_total) * 100
            threshold = mem_config["low_memory_threshold_percent"]
            logger.info(f"💾 현재 사용 가능한 메모리: {available_percent:.2f}% (임계치: {threshold}%)")

            if available_percent < threshold:
                run_command("sync; echo 3 > /proc/sys/vm/drop_caches")
        logger.info(f"[PASS] {section}")
    except Exception as e:
        logger.error(f"[FAIL] {section} | 오류: {e}")

# 4. 서비스 최적화
def optimize_services(service_config):
    section = "Services"
    try:
        for svc in service_config.get("disable_services", []):
            run_command(f"systemctl disable --now {svc}")

        zombie_cfg = service_config.get("zombie_cleanup", {})
        if zombie_cfg.get("enable"):
            zombie_found = False
            for proc in psutil.process_iter(['pid', 'ppid', 'name', 'status']):
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    zombie_found = True
                    logger.warning(f"⚠️ 좀비 프로세스: {proc.info}")
            if not zombie_found:
                logger.info("✅ 좀비 없음")
        logger.info(f"[PASS] {section}")
    except Exception as e:
        logger.error(f"[FAIL] {section} | 오류: {e}")

# 5. 보안 설정 강화
def harden_security(security_config):
    section = "Security"
    try:
        fw = security_config.get("firewall", {})
        if fw.get("enable"):
            if fw.get("deny_all_by_default", False):
                run_command("ufw default deny incoming")
            else:
                run_command("ufw default allow incoming")
            run_command("ufw default allow outgoing")
            for port in fw.get("blocked_ports", []):
                run_command(f"ufw deny in {port}")
                run_command(f"ufw deny out {port}")
            run_command("ufw enable")

        ssh = security_config.get("ssh", {})
        sshd_config = "/etc/ssh/sshd_config"
        for key, val in {
            "PermitRootLogin": ssh.get("permit_root_login"),
            "PasswordAuthentication": ssh.get("password_authentication"),
            "Protocol": ssh.get("protocol"),
            "MaxAuthTries": ssh.get("max_auth_tries")
        }.items():
            if val is not None:
                run_command(f"sed -i -E 's|^[#\\s]*{key}\\s+.*|{key} {val}|' {sshd_config}")
        run_command("systemctl restart sshd")

        logger.info(f"[PASS] {section}")
    except Exception as e:
        logger.error(f"[FAIL] {section} | 오류: {e}")

# 6. 디스크 최적화
def optimize_disk(disk_config):
    section = "Disk"
    try:
        if is_virtual_machine():
            logger.warning(f"[SKIP] {section} | 가상환경에서 생략")
            return

        # 디스크 조각 모음
        if disk_config.get("enable_defrag"):
            for path in disk_config.get("defrag_paths", []):
                run_command(f"e4defrag {path}")

        # 통합 정리 수행
        cleanup_cfg = disk_config.get("unified_cleanup", {})
        if cleanup_cfg.get("enable"):
            log_file = cleanup_cfg.get("log_file_path", "logs/unified_cleanup.log")
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            now = time.time()

            for root_path in cleanup_cfg.get("target_paths", []):
                for root, dirs, files in os.walk(root_path, topdown=False):
                    for f in files:
                        file_path = os.path.join(root, f)
                        try:
                            age_minutes = (now - os.path.getmtime(file_path)) / 60
                            if os.path.getsize(file_path) == 0 and age_minutes >= cleanup_cfg.get("min_file_age_minutes", 30):
                                os.remove(file_path)
                                with open(log_file, "a") as log:
                                    log.write(f"{time.ctime()} - Deleted empty file: {file_path}\n")
                        except Exception:
                            continue

                    if cleanup_cfg.get("remove_empty_dirs", True):
                        for d in dirs:
                            dir_path = os.path.join(root, d)
                            try:
                                if not os.listdir(dir_path):
                                    os.rmdir(dir_path)
                                    with open(log_file, "a") as log:
                                        log.write(f"{time.ctime()} - Deleted empty directory: {dir_path}\n")
                            except Exception:
                                continue

        logger.info(f"[PASS] {section}")
    except Exception as e:
        logger.error(f"[FAIL] {section} | 오류: {e}")


# 메인 최적화 실행
def optimize_system():
    config_loader = ConfigLoader("config/optimizer_settings.json")
    config_loader.load_config()
    config = config_loader.get_config()

    logger.info("시스템 최적화 시작")
    optimize_cpu(config["performance_optimization"]["cpu"])
    optimize_io(config["performance_optimization"]["io"])
    optimize_memory(config["memory_optimization"])
    optimize_services(config["service_management"])
    harden_security(config["security_hardening"])
    optimize_disk(config["disk_optimization"])
    logger.info("시스템 최적화 완료")

if __name__ == "__main__":
    optimize_system()

