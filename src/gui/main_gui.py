import tkinter as tk
from tkinter import messagebox, Toplevel, Checkbutton, IntVar
import subprocess
import sys
import os
import json
from pathlib import Path

CONFIG_PATH = Path("config/optimizer_settings.json")

def run_optimizer_with_feedback():
    """최적화 실행 후 결과를 시각적으로 보여주는 창 생성 (상태 텍스트 기반)"""
    result_window = Toplevel()
    result_window.title("최적화 진행 상태")
    result_window.geometry("400x350")

    status_labels = {}

    optim_items = ["CPU", "I/O", "Memory", "Services", "Disk", "Security"]
    for i, label in enumerate(optim_items):
        status_labels[label] = tk.Label(result_window, text=f"{label} 최적화: ⏳ 대기 중...", anchor="w")
        status_labels[label].grid(row=i, column=0, sticky="w", padx=10, pady=3)

    result_label = tk.Label(result_window, text="⌛ 최적화 중...", fg="blue")
    result_label.grid(row=len(optim_items), column=0, pady=10)

    try:
        # 최적화 실행 (여기선 단일 실행, 실제로는 모듈별 실행도 가능)
        result = subprocess.run("sudo PYTHONPATH=. python3 src/optimizer.py", shell=True, text=True, capture_output=True)

        # 로그 또는 출력에서 상태 감지 (실제 구문 파싱 또는 로그 기반 분석 필요)
        output = result.stdout + result.stderr

        for label in optim_items:
            if f"[PASS] {label}" in output:
                status_labels[label].config(text=f"{label} 최적화: ✅ 성공", fg="green")
            elif f"[SKIP] {label}" in output:
                status_labels[label].config(text=f"{label} 최적화: ⚠️ 건너뜀", fg="orange")
            else:
                status_labels[label].config(text=f"{label} 최적화: ❌ 실패", fg="red")

        if result.returncode == 0:
            result_label.config(text="✅ 전체 최적화 완료", fg="green")
        else:
            result_label.config(text="❌ 일부 최적화 실패", fg="red")

    except subprocess.CalledProcessError as e:
        result_label.config(text="❌ 최적화 실행 중 오류 발생", fg="red")
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
