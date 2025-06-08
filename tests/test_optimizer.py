import json
import os
import subprocess
from pathlib import Path

CONFIG_PATH = "config/optimizer_settings.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def snake_to_camel(snake):
    return ''.join(word.capitalize() for word in snake.split('_'))

def run_tests():
    config = load_config()
    results = {}

    # CPU
    try:
        cpu_cfg = config["performance_optimization"]["cpu"]
        governor_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
        if os.path.exists(governor_path):
            with open(governor_path) as f:
                current = f.read().strip()
            results["CPU"] = "✅" if current == cpu_cfg.get("governor") else "❌"
        else:
            results["CPU"] = "⚠️"
    except:
        results["CPU"] = "⚠️"

    # IO
    try:
        io_cfg = config["performance_optimization"]["io"]
        if not io_cfg.get("enable"):
            results["I/O"] = "⚠️"
        else:
            scheduler_path = "/sys/block/sda/queue/scheduler"
            if not os.path.exists(scheduler_path):
                results["I/O"] = "⚠️"
            else:
                sched = subprocess.getoutput(f"cat {scheduler_path}")
                read_ahead = subprocess.getoutput("blockdev --getra /dev/sda")
                sched_ok = io_cfg["scheduler"] in sched
                read_ok = str(io_cfg["read_ahead_kb"]) in read_ahead
                results["I/O"] = "✅" if sched_ok and read_ok else "❌"
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
            results["Firewall"] = "✅" if "Status: active" in status else "❌"
        else:
            results["Firewall"] = "✅" if "Status: inactive" in status else "❌"
    except:
        results["Firewall"] = "⚠️"

    # SSHD
    ssh_cfg = config.get("security_hardening", {}).get("ssh", {})
    sshd_path = "/etc/ssh/sshd_config"
    if not os.path.exists(sshd_path):
        results["SSHD"] = "⚠️"
    else:
        try:
            with open(sshd_path) as f:
                content = f.read()
            all_match = True
            for key, value in ssh_cfg.items():
                if key.lower() == "protocol":
                    continue  # Protocol은 최신 ssh 버전에서 불필요하므로 제외
                prop = snake_to_camel(key)
                if f"{prop} {value}" not in content and f"{prop}={value}" not in content:
                    all_match = False
                    break
            results["SSHD"] = "✅" if all_match else "❌"
        except:
            results["SSHD"] = "⚠️"

    # Disk
    try:
        disk_cfg = config["disk_optimization"]
        cleanup_cfg = disk_cfg.get("unified_cleanup", {})
        if not cleanup_cfg.get("enable"):
            results["Disk"] = "⚠️"
        else:
            log_path = cleanup_cfg.get("log_file_path", "/var/log/unified_cleanup.log")
            if not os.path.exists(log_path):
                results["Disk"] = "⚠️"
            else:
                with open(log_path) as f:
                    lines = f.readlines()
                    results["Disk"] = "✅" if len(lines) > 0 else "❌"
    except:
        results["Disk"] = "⚠️"

    return results

if __name__ == "__main__":
    results = run_tests()
    for category, status in results.items():
        print(f"{category} 최적화 결과: {status}")
