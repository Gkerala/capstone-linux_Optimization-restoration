import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

def launch_optimizer():
    try:
        subprocess.run("sudo PYTHONPATH=. python3 src/optimizer.py", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("오류", f"최적화 실행 실패:\n{e}")

def launch_restore():
    try:
        subprocess.Popen([sys.executable, "src/gui/restore_gui.py"])
    except Exception as e:
        messagebox.showerror("오류", f"복원 실행 GUI 실패: {e}")

def launch_optimizer_settings():
    try:
        subprocess.Popen([sys.executable, "src/gui/optimize_settings_gui.py"])
    except Exception as e:
        messagebox.showerror("오류", f"설정 GUI 실행 실패: {e}")

def launch_config_builder():
    try:
        subprocess.run([sys.executable, "config/config_builder.py"], check=True)
        messagebox.showinfo("설정 완료", "기본 설정 파일이 성공적으로 생성되었습니다.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("오류", f"기본 설정 설치 실패:\n{e}")

def main():
    root = tk.Tk()
    root.title("Linux Optimizer & Restore GUI")
    root.geometry("300x400")

    tk.Button(root, text="✨ 최적화 실행", height=2, command=launch_optimizer).pack(fill=tk.X, pady=5)
    tk.Button(root, text="♻️ 복원 실행", height=2, command=launch_restore).pack(fill=tk.X, pady=5)
    tk.Button(root, text="⚙️ 최적화 세팅", height=2, command=launch_optimizer_settings).pack(fill=tk.X, pady=5)
    tk.Button(root, text="📦 기본 설정 Install", height=2, command=launch_config_builder).pack(fill=tk.X, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
