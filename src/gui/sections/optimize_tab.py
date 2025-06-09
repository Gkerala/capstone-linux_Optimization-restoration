import tkinter as tk
from tkinter import Label
import subprocess
import threading
import os

optim_items = ["CPU", "I/O", "Memory", "Services", "Disk", "Security"]
status_labels = {}

def create_optimize_tab(notebook):
    frame = tk.Frame(notebook, padx=10, pady=10)

    # 상태 라벨 생성
    for i, item in enumerate(optim_items):
        status_labels[item] = Label(frame, text=f"{item} 최적화:")
        status_labels[item].grid(row=i, column=0, sticky="w", pady=5)

    result_label = Label(frame, text="")
    result_label.grid(row=len(optim_items) + 1, column=0, pady=10, sticky="w")

    def run_optimizer():
        def monitor():
            command = "sudo PYTHONPATH=. python3 src/optimizer.py"
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True
            )

            while True:
                line = process.stdout.readline()
                if not line:
                    break
                print("[DEBUG] 최적화 로그:", line.strip())

                for label in optim_items:
                    if f"[PASS] {label}" in line:
                        status_labels[label].config(text=f"{label} 최적화: ✅", fg="green")
                    elif f"[SKIP] {label}" in line:
                        status_labels[label].config(text=f"{label} 최적화: ⚠️", fg="orange")
                    elif f"[FAIL] {label}" in line or f"[ERROR] {label}" in line:
                        status_labels[label].config(text=f"{label} 최적화: ❌", fg="red")

            process.wait()
            if process.returncode == 0:
                result_label.config(text="✅ 최적화 완료", fg="green")
            else:
                result_label.config(text="❌ 일부 최적화 실패", fg="red")

        threading.Thread(target=monitor, daemon=True).start()

    # 실행 버튼
    run_btn = tk.Button(frame, text="▶ 최적화 실행", command=run_optimizer)
    run_btn.grid(row=len(optim_items), column=0, pady=10, sticky="w")

    return frame
