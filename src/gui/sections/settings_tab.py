import tkinter as tk
from tkinter import filedialog, messagebox
import json
from pathlib import Path
import subprocess

CONFIG_PATH = Path("config/optimizer_settings.json")

def load_restore_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        return config.get("restore_settings", {})
    return {}

def save_restore_config(restore_settings):
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
        else:
            config = {}
        config["restore_settings"] = restore_settings
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("저장 실패", f"설정 저장 중 오류 발생: {e}")
        return False

def create_settings_tab(notebook):
    frame = tk.Frame(notebook, padx=10, pady=10)
    restore_settings = load_restore_config()

    # 자동 백업 설정 체크박스
    auto_backup_var = tk.BooleanVar(value=restore_settings.get("auto_backup", True))
    tk.Checkbutton(frame, text="자동 백업 활성화", variable=auto_backup_var).pack(anchor="w")

    # 백업 경로 설정
    tk.Label(frame, text="백업 경로:").pack(anchor="w", pady=(10, 0))
    backup_path_var = tk.StringVar(value=restore_settings.get("backup_location", str(Path.home() / "backups")))
    entry_path = tk.Entry(frame, textvariable=backup_path_var, width=50)
    entry_path.pack(anchor="w")
    
    def choose_backup_path():
        path = filedialog.askdirectory(title="백업 경로 선택")
        if path:
            backup_path_var.set(path)

    tk.Button(frame, text="경로 선택", command=choose_backup_path).pack(anchor="w", pady=(0, 10))

    # 백업 주기 설정 (시간 단위)
    tk.Label(frame, text="자동 백업 주기 (시간 단위):").pack(anchor="w")
    backup_interval_var = tk.StringVar(value=str(restore_settings.get("backup_interval_hours", 24)))
    tk.Entry(frame, textvariable=backup_interval_var, width=10).pack(anchor="w")

    # 설정 저장 함수
    def save_settings():
        new_settings = {
            "auto_backup": auto_backup_var.get(),
            "backup_location": backup_path_var.get(),
            "backup_interval_hours": int(backup_interval_var.get()),
            "backup_format": restore_settings.get("backup_format", "zip"),
            "restore_cycle_days": restore_settings.get("restore_cycle_days", 7),
            "restore_points": restore_settings.get("restore_points", 5),
            "restore_targets": restore_settings.get("restore_targets", {}),
            "custom_backup": restore_settings.get("custom_backup", {})
        }

        if save_restore_config(new_settings):
            messagebox.showinfo("성공", "설정이 저장되었습니다.")

    # 저장 버튼
    tk.Button(frame, text=" 설정 저장", command=save_settings).pack(anchor="w", pady=10)

    # 기본 설정 설치 버튼
    def install_defaults():
        try:
            subprocess.run(["python3", "src/utils/config_builder.py"], check=True)
            messagebox.showinfo("성공", "기본 설정이 생성되었습니다.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("실패", f"기본 설정 생성 실패:\n{e}")

    tk.Button(frame, text="기본 설정 재설치", command=install_defaults).pack(anchor="w", pady=5)
    
    # 설정 변경 버튼 → optimize_settings_gui.py 실행
    def launch_optimize_settings():
        try:
            subprocess.Popen(["python3", "src/gui/optimize_settings_gui.py"])
        except Exception as e:
           messagebox.showerror("오류", f"설정 GUI 실행 실패: {e}")

    tk.Button(frame, text="설정 변경", command=launch_optimize_settings).pack(anchor="w", pady=5)


    return frame
