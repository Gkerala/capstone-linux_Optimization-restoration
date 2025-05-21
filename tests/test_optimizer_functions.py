# test_optimizer_functions.py
# 각 최적화 기능들이 실제로 잘 동작하는지 검증하는 테스트 코드입니다.

import os
import subprocess
import psutil
from src.optimizer import (
    optimize_cpu,
    optimize_io,
    optimize_memory,
    optimize_services,
    harden_security,
    optimize_disk
)
from src.utils.config import ConfigLoader

# 명령 실행 결과 캡처

def run_and_capture(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"\n[Command] {command}")
        print(result.stdout)
        if result.stderr:
            print("[Error]", result.stderr)
    except Exception as e:
        print(f"[Exception] {command} 실행 중 오류: {e}")

# 1. CPU 최적화 테스트
def test_cpu_optimization(config):
    print("\n=== CPU 최적화 테스트 ===")
    optimize_cpu(config["performance_optimization"]["cpu"])
    run_and_capture("chrt -p $(pgrep -f python3 | head -n 1)")
    run_and_capture("renice -n -5 -p $(pgrep -f python3 | head -n 1)")

# 2. IO 최적화 테스트
def test_io_optimization(config):
    print("\n=== IO 최적화 테스트 ===")
    optimize_io(config["performance_optimization"]["io"])
    run_and_capture("cat /sys/block/sda/queue/scheduler")
    run_and_capture("blockdev --getra /dev/sda")

# 3. 메모리 최적화 테스트
def test_memory_optimization(config):
    print("\n=== 메모리 최적화 테스트 ===")
    optimize_memory(config["memory_optimization"])
    run_and_capture("free -m")

# 4. 서비스 최적화 테스트
def test_service_optimization(config):
    print("\n=== 서비스 최적화 테스트 ===")
    optimize_services(config["service_management"])
    run_and_capture("systemctl list-unit-files --state=disabled")

# 5. 보안 설정 테스트
def test_security_hardening(config):
    print("\n=== 보안 설정 테스트 ===")
    harden_security(config["security_hardening"])
    run_and_capture("ufw status verbose")
    run_and_capture("cat /etc/ssh/sshd_config | grep -E 'PermitRootLogin|PasswordAuthentication|Protocol|MaxAuthTries'")

# 6. 디스크 최적화 테스트
def test_disk_optimization(config):
    print("\n=== 디스크 최적화 테스트 ===")
    optimize_disk(config["disk_optimization"])
    run_and_capture("tail -n 10 /var/log/inode_cleanup.log")
    run_and_capture("tail -n 10 /var/log/temp_cleanup.log")

# 전체 테스트 실행
def run_all_tests():
    config_loader = ConfigLoader("config/optimizer_settings.json")
    config_loader.load_config()
    config = config_loader.get_config()

    test_cpu_optimization(config)
    test_io_optimization(config)
    test_memory_optimization(config)
    test_service_optimization(config)
    test_security_hardening(config)
    test_disk_optimization(config)

if __name__ == "__main__":
    run_all_tests()
