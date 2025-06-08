import tkinter as tk
from tkinter import messagebox, Toplevel
import subprocess
import sys
sys.path.append('.')
from tests.test_optimizer import run_tests  # 최적화 테스트 모듈 임포트

def show_optimization_result():
    result_window = Toplevel()
    result_window.title("최적화 결과 상태")
    result_window.geometry("400x400")

    try:
        # 최적화 실행
        subprocess.run("sudo PYTHONPATH=. python3 src/optimizer.py", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("오류", f"최적화 실행 실패:\n{e}")
        return

    try:
        result_data = run_tests()  # 예: {"CPU": "✅", "Disk": "❌", ...}
    except Exception as e:
        messagebox.showerror("오류", f"최적화 테스트 실패: {e}")
        return

    row = 0
    for key, val in result_data.items():
        if isinstance(val, dict):
            tk.Label(result_window, text=f"{key} 최적화 결과:", font=("Arial", 11, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=3)
            row += 1
            for sub_key, sub_val in val.items():
                tk.Label(result_window, text=f"    {sub_key} : {sub_val}", font=("Arial", 10)).grid(row=row, column=0, sticky="w", padx=20)
                row += 1
        else:
            tk.Label(result_window, text=f"{key} 최적화 결과: {val}", font=("Arial", 11)).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            row += 1

    tk.Label(result_window, text="✔️ 최적화 테스트 완료", fg="green").grid(row=row, column=0, pady=10)

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

    tk.Button(root, text="✨ 최적화 실행", height=2, command=show_optimization_result).pack(fill=tk.X, pady=5)
    tk.Button(root, text="♻️ 복원 실행", height=2, command=launch_restore).pack(fill=tk.X, pady=5)
    tk.Button(root, text="⚙️ 최적화 세팅", height=2, command=launch_optimizer_settings).pack(fill=tk.X, pady=5)
    tk.Button(root, text="📦 기본 설정 Install", height=2, command=launch_config_builder).pack(fill=tk.X, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
