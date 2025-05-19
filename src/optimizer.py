import os
import subprocess
from src.utils.logger import get_logger
from src.utils.config import ConfigLoader
from src.utils.system import is_virtual_machine
import psutil  

logger = get_logger(__name__)

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        logger.info(f"[OK] {command}")
    except subprocess.CalledProcessError as e:
        logger.error(f"[FAIL] {command} | 오류: {e}")

# 1. CPU 최적화
def optimize_cpu(cpu_config):
    if is_virtual_machine():
        logger.warning("⚠️ 가상 환경에서는 CPU governor 설정을 건너뜁니다.")
    else:
        if cpu_config.get("governor"):
            governor = cpu_config["governor"]
            run_command(f"cpupower frequency-set -g {governor}")

    for proc in cpu_config.get("priority_processes", []):
        run_command(f"renice -n -5 -p $(pgrep {proc} | head -n 1)")

    if cpu_config.get("enable_scheduler_tuning"):
        scheduler_policy = cpu_config.get("scheduler_policy", "SCHED_OTHER")
        policy_map = {
            "SCHED_FIFO": "-f",
            "SCHED_RR": "-r",
            "SCHED_BATCH": "-b",
            "SCHED_IDLE": "-i",
            "SCHED_OTHER": ""  
        }
        option = policy_map.get(scheduler_policy.upper(), None)

        if option is None:
            logger.warning(f"⚠️ 알 수 없는 scheduler_policy: {scheduler_policy}")
            return

        for proc in cpu_config.get("target_processes", []):
            run_command(f"chrt {option} -p 50 $(pgrep {proc} | head -n 1) && chrt -p $(pgrep {proc} | head -n 1)")


# 2. IO 최적화
def optimize_io(io_config):
    if is_virtual_machine():
        logger.warning("⚠️ 가상 환경에서는 I/O 스케줄러 최적화를 건너뜁니다.")
        return

    if io_config.get("enable"):
        scheduler = io_config.get("scheduler", "deadline")
        run_command(f"echo {scheduler} | tee /sys/block/sda/queue/scheduler")
        read_ahead = io_config.get("read_ahead_kb", 128)
        run_command(f"blockdev --setra {read_ahead} /dev/sda")

# 3. 메모리 최적화
def optimize_memory(mem_config):
    if "swappiness" in mem_config:
        run_command(f"sysctl vm.swappiness={mem_config['swappiness']}")

    if mem_config.get("drop_caches_on_schedule") and mem_config.get("drop_cache_mode") is not None:
        run_command(f"sync; echo {mem_config['drop_cache_mode']} > /proc/sys/vm/drop_caches")

    if "low_memory_threshold_percent" in mem_config:
        try:
            with open('/proc/meminfo') as f:
                meminfo = f.read()
            mem_total = int(re.search(r'MemTotal:\s+(\d+)', meminfo).group(1))
            mem_available = int(re.search(r'MemAvailable:\s+(\d+)', meminfo).group(1))
            available_percent = (mem_available / mem_total) * 100

            threshold = mem_config["low_memory_threshold_percent"]
            logger.info(f"💾 현재 사용 가능한 메모리: {available_percent:.2f}% (임계치: {threshold}%)")

            if available_percent < threshold:
                logger.info("⚠️ 메모리 부족 — 조건부 캐시 삭제 수행")
                run_command("sync; echo 3 > /proc/sys/vm/drop_caches")
            else:
                logger.info("✅ 메모리 충분 — 조건부 캐시 삭제 생략")
        except Exception as e:
            logger.warning(f"⚠️ 메모리 최적화 조건부 처리 중 오류 발생: {e}")
            
# 4. 서비스 최적화
def optimize_services(service_config):
    for service in service_config.get("disable_services", []):
        run_command(f"systemctl disable --now {service}")
        
    zombie_cfg = service_config.get("zombie_cleanup", {})
    if zombie_cfg.get("enable"):
        logger.info("🧟 좀비 프로세스 상태 확인 중...")
        zombie_found = False
        for proc in psutil.process_iter(['pid', 'ppid', 'name', 'status']):
            try:
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    zombie_found = True
                    logger.warning(
                        f"⚠️ 좀비 프로세스 감지됨 - PID: {proc.info['pid']}, "
                        f"PPID: {proc.info['ppid']}, NAME: {proc.info['name']}"
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not zombie_found:
            logger.info("✅ 현재 좀비 프로세스 없음.")

# 5. 보안 설정 강화
def harden_security(security_config):
    fw = security_config.get("firewall", {})
    if fw.get("enable"):
        run_command("ufw default deny")
        for port in fw.get("allowed_ports", []):
            run_command(f"ufw allow {port}")
        run_command("ufw enable")

    ssh = security_config.get("ssh", {})
    sshd_config_path = "/etc/ssh/sshd_config"
    replace_lines = {
        "PermitRootLogin": ssh.get("permit_root_login"),
        "PasswordAuthentication": ssh.get("password_authentication"),
        "Protocol": ssh.get("protocol"),
        "MaxAuthTries": ssh.get("max_auth_tries")
    }

    for key, val in replace_lines.items():
    	if val is not None:
        	run_command(f"sed -i -E 's|^[#\\s]*{key}\\s+.*|{key} {val}|' {sshd_config_path}")

    run_command("systemctl restart sshd")

# 6. 디스크 최적화
def optimize_disk(disk_config):
    if is_virtual_machine():
        logger.warning("⚠️ 가상 환경에서는 디스크 조각 모음/스케줄러는 건너뜁니다.")
        return

    if disk_config.get("enable_defrag"):
        for path in disk_config.get("defrag_paths", []):
            run_command(f"e4defrag {path}")

    inode_cfg = disk_config.get("inode_cleanup", {})
    if inode_cfg.get("enable"):
        for path in inode_cfg.get("target_paths", []):
            run_command(f"find {path} -type f -empty -delete")
            if inode_cfg.get("remove_empty_dirs"):
                run_command(f"find {path} -type d -empty -delete")

# 메인 함수
def optimize_system():
    config_path = "config/optimizer_settings.json"
    config_loader = ConfigLoader(config_path)
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
    return "최적화 완료"

if __name__ == "__main__":
    optimize_system()

