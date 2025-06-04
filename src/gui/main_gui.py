import tkinter as tk
from tkinter import messagebox, Toplevel, Checkbutton, IntVar
import subprocess
import sys
import os
import json
from pathlib import Path

CONFIG_PATH = Path("config/optimizer_settings.json")

def run_optimizer_with_feedback():
    """최적화 실행 후 결과를 시각적으로 보여주는 창 생성"""
    result_window = Toplevel()
    result_window.title("최적화 진행 상태")
    result_window.geometry("400x350")

    # 최적화 기능 상태 확인용 체크박스 변수 저장
    optimization_checks = {
        "CPU": IntVar(),
        "I/O": IntVar(),
        "Memory": IntVar(),
        "Services": IntVar(),
        "Disk": IntVar(),
        "Security": IntVar()
    }

    for i, (label, var) in enumerate(optimization_checks.items()):
        cb = Checkbutton(result_window, text=label + " 최적화", variable=var)
        cb.grid(row=i, column=0, sticky="w", padx=10, pady=5)

    try:
        # 실제 최적화 실행
        subprocess.run("sudo PYTHONPATH=. python3 src/optimizer.py", shell=True, check=True)
        # 실행 후 체크 표시 (시뮬레이션)
        for var in optimization_checks.values():
            var.set(1)

        tk.Label(result_window, text="✅ 최적화 완료.", fg="green").grid(row=len(optimization_checks), column=0, pady=10)

    except subprocess.CalledProcessError as e:
        messagebox.showerror("오류", f"최적화 실행 실패:\n{e}")
        tk.Label(result_window, text="❌ 최적화 실패.", fg="red").grid(row=len(optimization_checks), column=0, pady=10)

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
        subprocess.run([sys.executable, "src/utils/config_builder.py"], check=True)
        messagebox.showinfo("설정 완료", "기본 설정 파일이 성공적으로 생성되었습니다.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("오류", f"기본 설정 설치 실패:\n{e}")

def main():
    root = tk.Tk()
    root.title("Linux Optimizer & Restore GUI")
    root.geometry("300x400")

    tk.Button(root, text="✨ 최적화 실행", height=2, command=run_optimizer_with_feedback).pack(fill=tk.X, pady=5)
    tk.Button(root, text="♻️ 복원 실행", height=2, command=launch_restore).pack(fill=tk.X, pady=5)
    tk.Button(root, text="⚙️ 최적화 세팅", height=2, command=launch_optimizer_settings).pack(fill=tk.X, pady=5)
    tk.Button(root, text="📦 기본 설정 Install", height=2, command=launch_config_builder).pack(fill=tk.X, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
