import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import subprocess
import os
from pathlib import Path

CUSTOM_BACKUP_DIR = Path("custom_backups")
TIMESHIFT_CMD = "timeshift"

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def custom_backup():
    path = filedialog.askopenfilename(title="백업할 파일 선택")
    if not path:
        return "백업이 취소되었습니다."
    os.makedirs(CUSTOM_BACKUP_DIR, exist_ok=True)
    dest = CUSTOM_BACKUP_DIR / Path(path).name
    try:
        subprocess.run(f"cp '{path}' '{dest}'", shell=True, check=True)
        return f"✅ 백업 완료: {dest}"
    except Exception as e:
        return f"❌ 백업 실패: {e}"

def list_custom_backups():
    if not CUSTOM_BACKUP_DIR.exists():
        return "❌ 백업 없음"
    return "\n".join(f"- {f.name}" for f in CUSTOM_BACKUP_DIR.iterdir())

def restore_custom_backup():
    file = filedialog.askopenfilename(initialdir=str(CUSTOM_BACKUP_DIR), title="복원할 백업 파일 선택")
    if not file:
        return "복원 취소됨."
    dest = filedialog.askdirectory(title="복원할 위치 선택")
    if not dest:
        return "복원 취소됨."
    try:
        subprocess.run(f"cp '{file}' '{dest}'", shell=True, check=True)
        return f"✅ 복원 완료: {file} -> {dest}"
    except Exception as e:
        return f"❌ 복원 실패: {e}"

def delete_custom_backup():
    file = filedialog.askopenfilename(initialdir=str(CUSTOM_BACKUP_DIR), title="삭제할 백업 파일 선택")
    if not file:
        return "삭제 취소됨."
    try:
        os.remove(file)
        return f"✅ 삭제 완료: {file}"
    except Exception as e:
        return f"❌ 삭제 실패: {e}"

def create_timeshift_snapshot():
    out, err = run_command(f"sudo {TIMESHIFT_CMD} --create")
    return err if err else out

def list_timeshift_snapshots():
    out, err = run_command(f"sudo {TIMESHIFT_CMD} --list")
    return err if err else out

def restore_timeshift():
    return "🔧 Timeshift 복원은 CLI에서 수동 복원 권장 (timeshift --restore)"

def delete_timeshift():
    return "🔧 Timeshift 스냅샷 삭제는 CLI에서 수동 삭제 권장 (timeshift --delete)"

class RestoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Restore Options")
        self.root.geometry("500x500")

        self.output_box = tk.Text(root, height=25)
        self.output_box.pack(fill=tk.BOTH, expand=True)

        self.input_box = tk.Entry(root)
        self.input_box.pack(fill=tk.X)
        self.input_box.bind("<Return>", self.handle_input)

        self.print_instructions()

    def print_instructions(self):
        instructions = (
            "==== 복원 기능 선택 ===="
            "\n1. 사용자 정의 백업 생성"
            "\n2. 사용자 정의 백업 목록 확인"
            "\n3. 사용자 정의 백업 복원"
            "\n4. 사용자 정의 백업 삭제"
            "\n5. Timeshift 스냅샷 생성"
            "\n6. Timeshift 스냅샷 목록 확인"
            "\n7. Timeshift 복원 (수동)"
            "\n8. Timeshift 삭제 (수동)"
        )
        self.output_box.insert(tk.END, instructions + "\n\n")

    def handle_input(self, event):
        choice = self.input_box.get().strip()
        self.input_box.delete(0, tk.END)

        if choice == "1":
            result = custom_backup()
        elif choice == "2":
            result = list_custom_backups()
        elif choice == "3":
            result = restore_custom_backup()
        elif choice == "4":
            result = delete_custom_backup()
        elif choice == "5":
            result = create_timeshift_snapshot()
        elif choice == "6":
            result = list_timeshift_snapshots()
        elif choice == "7":
            result = restore_timeshift()
        elif choice == "8":
            result = delete_timeshift()
        else:
            result = "❌ 잘못된 선택"

        self.output_box.insert(tk.END, f"\n[결과]\n{result}\n\n")
        self.output_box.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = RestoreGUI(root)
    root.mainloop()
