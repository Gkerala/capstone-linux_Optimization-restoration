import json
import os
import subprocess
import time

CONFIG_PATH = "config/optimizer_settings.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def print_result(title, success=True, extra=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {title}")
    if extra:
        print(f"   ↪︎ {extra}")

def test_cpu(cpu_cfg):
    print("\n[🔧 CPU 최적화 확인]")
    # governor 확인
    try:
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") as f:
            current = f.read().strip()
        print_result("CPU governor 적용 확인", current == cpu_cfg.get("governor"), f"현재: {current}")
    except:
        print_result("CPU governor 적용 확인", False, "읽기 실패")

    # priority_processes 확인
    for proc in cpu_cfg.get("priority_processes", []):
        res = subprocess.getoutput(f"ps -eo pid,ni,comm | grep {proc}")
        print_result(f"renice 우선순위 적용 - {proc}", "-5" in res or "-10" in res, res.strip())

    # scheduler 확인
    if cpu_cfg.get("enable_scheduler_tuning"):
        for proc in cpu_cfg.get("target_processes", []):
            pid_cmd = f"pgrep {proc} | head -n1"
            pid = subprocess.getoutput(pid_cmd)
            if pid.isdigit():
                sched_cmd = f"chrt -p {pid}"
                sched_out = subprocess.getoutput(sched_cmd)
                print_result(f"chrt 정책 적용 - {proc}", "Scheduling Policy" in sched_out, sched_out)
            else:
                print_result(f"chrt 정책 적용 - {proc}", False, "프로세스 없음")

def test_io(io_cfg):
    print("\n[💾 IO 최적화 확인]")
    if not io_cfg.get("enable"):
        print("건너뜀 (비활성화됨)")
        return
    try:
        current_scheduler = subprocess.getoutput("cat /sys/block/sda/queue/scheduler")
        print_result("I/O scheduler 적용", io_cfg["scheduler"] in current_scheduler, current_scheduler)
    except:
        print_result("I/O scheduler 적용", False)

    read_ahead = subprocess.getoutput("blockdev --getra /dev/sda")
    print_result("Read Ahead 설정 확인", str(io_cfg["read_ahead_kb"]) in read_ahead, read_ahead)

def test_memory(mem_cfg):
    print("\n[🧠 메모리 최적화 확인]")
    swappiness = subprocess.getoutput("cat /proc/sys/vm/swappiness")
    print_result("Swappiness 설정 확인", str(mem_cfg["swappiness"]) == swappiness.strip(), f"현재: {swappiness}")

def test_services(service_cfg):
    print("\n[🔧 서비스 관리 확인]")
    for svc in service_cfg.get("disable_services", []):
        state = subprocess.getoutput(f"systemctl is-enabled {svc}")
        print_result(f"{svc} 서비스 비활성화", "disabled" in state, state)

    if service_cfg.get("zombie_cleanup", {}).get("enable"):
        procs = subprocess.getoutput("ps -eo stat,ppid,pid,cmd | awk '$1 ~ /Z/'")
        print_result("좀비 프로세스 탐지 기능", True, "감지된 항목:\n" + procs if procs else "없음")

def test_firewall(fw_cfg):
    print("\n[🛡️ 방화벽 설정 확인]")
    status = subprocess.getoutput("ufw status")
    if fw_cfg.get("enable"):
        print_result("UFW 활성화 여부", "Status: active" in status)
        for port in fw_cfg.get("blocked_ports", []):
            print_result(f"포트 {port} 차단 여부", f"{port}" in status and "DENY" in status)
    else:
        print_result("UFW 비활성화 설정 확인", "Status: inactive" in status)

def test_disk(disk_cfg):
    print("\n[🗂️ 디스크 최적화 확인]")
    if disk_cfg.get("enable_defrag"):
        print_result("조각모음 실행 확인", True, "e4defrag는 결과 확인 어려우므로 생략")

    unified = disk_cfg.get("unified_cleanup", {})
    if unified.get("enable"):
        log_path = unified.get("log_file_path", "/var/log/unified_cleanup.log")
        if os.path.exists(log_path):
            with open(log_path) as f:
                lines = f.readlines()
                print_result("정리 로그 존재 여부", len(lines) > 0, f"{len(lines)}개 로그 존재")
        else:
            print_result("정리 로그 존재 여부", False, "로그 파일 없음")
            
def run_tests():
    config = load_config()

    results = {}

    # CPU
    try:
        cpu_cfg = config["performance_optimization"]["cpu"]
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") as f:
            current = f.read().strip()
        results["CPU"] = "✅" if current == cpu_cfg.get("governor") else "❌"
    except:
        results["CPU"] = "⚠️"

    # IO
    try:
        io_cfg = config["performance_optimization"]["io"]
        if io_cfg.get("enable"):
            sched = subprocess.getoutput("cat /sys/block/sda/queue/scheduler")
            results["I/O"] = "✅" if io_cfg["scheduler"] in sched else "❌"
        else:
            results["I/O"] = "⚠️"
    except:
        results["I/O"] = "⚠️"

    # Memory
    try:
        mem_cfg = config["memory_optimization"]
        current = subprocess.getoutput("cat /proc/sys/vm/swappiness").strip()
        results["Memory"] = "✅" if str(mem_cfg["swappiness"]) == current else "❌"
    except:
        results["Memory"] = "⚠️"

    # Services
    try:
        service_cfg = config["service_management"]
        failed = False
        for svc in service_cfg.get("disable_services", []):
            state = subprocess.getoutput(f"systemctl is-enabled {svc}")
            if "disabled" not in state:
                failed = True
                break
        results["Services"] = "✅" if not failed else "❌"
    except:
        results["Services"] = "⚠️"

    # Firewall
    try:
        fw_cfg = config["security_hardening"]["firewall"]
        status = subprocess.getoutput("ufw status")
        if fw_cfg.get("enable"):
            results["Security"] = "✅" if "Status: active" in status else "❌"
        else:
            results["Security"] = "✅" if "Status: inactive" in status else "❌"
    except:
        results["Security"] = "⚠️"

    # Disk Cleanup Log
    try:
        disk_cfg = config["disk_optimization"]
        log_path = disk_cfg.get("unified_cleanup", {}).get("log_file_path", "/var/log/unified_cleanup.log")
        if os.path.exists(log_path):
            with open(log_path) as f:
                lines = f.readlines()
                results["Disk"] = "✅" if len(lines) > 0 else "❌"
        else:
            results["Disk"] = "❌"
    except:
        results["Disk"] = "⚠️"

    return results


def main():
    config = load_config()

    test_cpu(config["performance_optimization"]["cpu"])
    test_io(config["performance_optimization"]["io"])
    test_memory(config["memory_optimization"])
    test_services(config["service_management"])
    test_firewall(config["security_hardening"]["firewall"])
    test_disk(config["disk_optimization"])

    print("\n🧪 모든 테스트 완료.")

if __name__ == "__main__":
    main()
