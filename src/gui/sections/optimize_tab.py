import tkinter as tk
from tkinter import Label
import subprocess
import threading

# 최적화 항목 리스트
OPTIMIZATION_CATEGORIES = ["CPU", "I/O", "Memory", "Services", "Security", "Disk"]

# 각 항목별 상태 표시 라벨 저장
status_labels = {}

def create_optimize_tab(notebook):
    frame = tk.Frame(notebook, padx=10, pady=10)

    # 라벨 UI 생성
    for idx, category in enumerate(OPTIMIZATION_CATEGORIES):
        label = Label(frame, text=f"{category}: ⏳ 대기 중...", anchor="w", width=40, font=("Arial", 11))
        label.grid(row=idx, column=0, sticky="w", padx=10, pady=5)
        status_labels[category] = label

    # 최종 결과 라벨
    result_label = Label(frame, text="", font=("Arial", 11, "bold"))
    result_label.grid(row=len(OPTIMIZATION_CATEGORIES), column=0, pady=10)

    # 최적화 실행 함수
    def run_optimization():
        def monitor():
            process = subprocess.Popen(
                ["sudo", "PYTHONPATH=.", "python3", "src/optimizer.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            success = True
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                print("[DEBUG]", line.strip())  # 디버깅 로그

                for category in OPTIMIZATION_CATEGORIES:
                    if f"[PASS] {category}" in line:
                        status_labels[category].config(text=f"{category}: ✅ 성공", fg="green")
                    elif f"[SKIP] {category}" in line:
                        status_labels[category].config(text=f"{category}: ⚠️ 생략됨", fg="orange")
                    elif f"[FAIL] {category}" in line:
                        status_labels[category].config(text=f"{category}: ❌ 실패", fg="red")
                        success = False

            process.wait()

            if success and process.returncode == 0:
                result_label.config(text="✅ 모든 최적화가 성공적으로 완료되었습니다.", fg="green")
            else:
                result_label.config(text="❌ 일부 최적화 실패", fg="red")

        # 백그라운드 스레드에서 실행
        threading.Thread(target=monitor, daemon=True).start()

    # 실행 버튼
    run_btn = tk.Button(frame, text="▶ 최적화 실행", command=run_optimization)
    run_btn.grid(row=len(OPTIMIZATION_CATEGORIES) + 1, column=0, pady=10)

    return frame
