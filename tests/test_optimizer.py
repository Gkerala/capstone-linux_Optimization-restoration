import unittest
from unittest.mock import patch
from src import optimizer

class TestOptimizer(unittest.TestCase):

    @patch("src.optimizer.run_command")
    def test_optimize_cpu(self, mock_run):
        config = {
            "enable_scheduler_tuning": False,
            "governor": "performance",
            "priority_processes": ["python3", "nginx"]
        }
        optimizer.optimize_cpu(config)
        mock_run.assert_any_call("cpupower frequency-set -g performance")
        mock_run.assert_any_call("renice -n -5 -p $(pgrep python3 | head -n 1)")
        mock_run.assert_any_call("renice -n -5 -p $(pgrep nginx | head -n 1)")
        self.assertEqual(mock_run.call_count, 3)

    @patch("src.optimizer.run_command")
    def test_optimize_io(self, mock_run):
        config = {
            "enable": True,
            "scheduler": "deadline",
            "read_ahead_kb": 128
        }
        optimizer.optimize_io(config)
        mock_run.assert_any_call("echo deadline | tee /sys/block/sda/queue/scheduler")
        mock_run.assert_any_call("blockdev --setra 128 /dev/sda")
        self.assertEqual(mock_run.call_count, 2)

    @patch("src.optimizer.run_command")
    def test_optimize_memory(self, mock_run):
        config = {
            "swappiness": 10,
            "drop_caches_on_schedule": True,
            "drop_cache_mode": 3
        }
        optimizer.optimize_memory(config)
        mock_run.assert_any_call("sysctl vm.swappiness=10")
        mock_run.assert_any_call("sync; echo 3 > /proc/sys/vm/drop_caches")
        self.assertEqual(mock_run.call_count, 2)

    @patch("src.optimizer.run_command")
    def test_optimize_services(self, mock_run):
        config = {
            "disable_services": ["cups", "bluetooth", "avahi-daemon"]
        }
        optimizer.optimize_services(config)
        for service in config["disable_services"]:
            mock_run.assert_any_call(f"systemctl disable --now {service}")
        self.assertEqual(mock_run.call_count, 3)

    @patch("src.optimizer.run_command")
    def test_harden_security(self, mock_run):
        config = {
            "firewall": {
                "enable": True,
                "allowed_ports": [22, 80, 443],
                "deny_all_by_default": True
            },
            "ssh": {
                "permit_root_login": "no",
                "password_authentication": "no",
                "protocol": 2,
                "max_auth_tries": 3
            }
        }
        optimizer.harden_security(config)

        mock_run.assert_any_call("ufw default deny")
        mock_run.assert_any_call("ufw allow 22")
        mock_run.assert_any_call("ufw allow 80")
        mock_run.assert_any_call("ufw allow 443")
        mock_run.assert_any_call("ufw enable")

        ssh_expected_cmds = [
            "sed -i 's/^#?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config",
            "sed -i 's/^#?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config",
            "sed -i 's/^#?Protocol.*/Protocol 2/' /etc/ssh/sshd_config",
            "sed -i 's/^#?MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config",
            "systemctl restart sshd"
        ]
        for cmd in ssh_expected_cmds:
            mock_run.assert_any_call(cmd)
        self.assertEqual(mock_run.call_count, 10)

    @patch("src.optimizer.run_command")
    def test_optimize_disk(self, mock_run):
        config = {
            "enable_defrag": True,
            "defrag_paths": ["/home", "/var"],
            "inode_cleanup": {
                "enable": True,
                "target_paths": ["/tmp", "/var/tmp"],
                "remove_empty_dirs": True
            }
        }
        optimizer.optimize_disk(config)
        mock_run.assert_any_call("e4defrag /home")
        mock_run.assert_any_call("e4defrag /var")
        mock_run.assert_any_call("find /tmp -type f -empty -delete")
        mock_run.assert_any_call("find /var/tmp -type f -empty -delete")
        mock_run.assert_any_call("find /tmp -type d -empty -delete")
        mock_run.assert_any_call("find /var/tmp -type d -empty -delete")
        self.assertEqual(mock_run.call_count, 6)


if __name__ == "__main__":
    unittest.main()

