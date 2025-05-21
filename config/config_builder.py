import platform
import psutil
import subprocess
import json
import os
from pathlib import Path

def get_filesystem_type():
    try:
        result = subprocess.run(['df', '-T', '/'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        if len(lines) > 1:
            filesystem_type = lines[1].split()[1]
            return filesystem_type
    except Exception as e:
        print(f"파일 시스템 감지 오류: {e}")
    return "ext4"

def get_system_info():
    return {
        "os": "Linux",
        "architecture": platform.architecture()[0],
        "cpu_count": psutil.cpu_count(logical=True),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "disk_usage": {
            "total_gb": round(psutil.disk_usage('/').total / (1024 ** 3), 2),
            "used_gb": round(psutil.disk_usage('/').used / (1024 ** 3), 2),
            "free_gb": round(psutil.disk_usage('/').free / (1024 ** 3), 2),
            "usage_percent": psutil.disk_usage('/').percent
        },
        "network_interfaces": list(psutil.net_if_addrs().keys()),
        "filesystem": {
            "root_partition": "/",
            "filesystem_type": get_filesystem_type()
        }
    }

def get_optimizer_settings():
    backup_location = Path.home() / "backups"
    backup_location.mkdir(parents=True, exist_ok=True)

    return {
        "performance_optimization": {
            "cpu": {
                "enable_scheduler_tuning": True,
                "governor": "performance",
                "priority_processes": ["python3", "nginx"],
                "scheduler_policy": "SCHED_FIFO",
                "target_processes": ["python3"]
            },
            "io": {
                "enable": True,
                "scheduler": "deadline",
                "read_ahead_kb": 128
            }
        },

        "memory_optimization": {
            "swappiness": 10,
            "drop_caches_on_schedule": True,
            "drop_cache_mode": "3",
            "low_memory_threshold_percent": 15
        },

        "service_management": {
            "disable_services": ["cups", "bluetooth", "avahi-daemon"],
            "zombie_cleanup": {
                "enable": True,
                "check_interval_minutes": 30
            }
        },

        "automation": {
            "use_crontab": True,
            "scheduled_tasks": [
                {
                    "name": "memory_cache_cleaner",
                    "schedule": "0 */6 * * *",
                    "command": "sync; echo 3 > /proc/sys/vm/drop_caches"
                },
                {
                    "name": "zombie_checker",
                    "schedule": "*/30 * * * *",
                    "command": "ps -eo stat,ppid | awk '$1 ~ /Z/ { print $2 }' | xargs -r kill -9"
                }
            ]
        },

        "security_hardening": {
            "firewall": {
                "enable": true,
                "blocked_ports": [8888, 9999, 7777],
                "deny_all_by_default": true
            },
            "ssh": {
                "permit_root_login": "no",
                "password_authentication": "no",
                "protocol": 2,
                "max_auth_tries": 3
            }
        },

        "disk_optimization": {
            "enable_defrag": True,
            "defrag_paths": ["/home", "/var"],

            "unified_cleanup": {
                "enable": true,
                "target_paths": [
                "/tmp",
                "/download",
                "/var/tmp",
                "/var/cache/apt/archives"
                ],
                "min_file_age_minutes": 30,
                "remove_empty_dirs": true,
                "log_file_path": "/var/log/unified_cleanup.log"
            }
        },

        "restore_settings": {
            "auto_backup": True,
            "backup_interval_hours": 24,
            "backup_location": str(backup_location),
            "backup_format": "zip",
            "restore_cycle_days": 7,
            "restore_points": 5
        },

        "log_management": {
            "enable": True,
            "log_level": "INFO",
            "log_file_path": str(Path("logs/system.log")),
            "max_log_size_mb": 50
        },

        "notification_settings": {
            "enable": True,
            "notify_on_completion": True,
            "notify_on_failure": True,
            "notification_method": ["email", "desktop"]
        },

        "custom_settings": {
            "user_defined_options": {}
        }
    }

def save_to_file(data, filename):
    config_path = Path("config") / filename
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"✅ {filename} 저장 완료")

def main():
    system_info = get_system_info()
    optimizer_settings = get_optimizer_settings()

    save_to_file(system_info, "system_info.json")
    save_to_file(optimizer_settings, "optimizer_settings.json")

if __name__ == "__main__":
    main()

