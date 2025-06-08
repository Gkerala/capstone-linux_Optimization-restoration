import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from pathlib import Path
import sys
sys.path.append('.')
from src.restore import (
    custom_backup,
    list_custom_backups,
    restore_custom_backup,
    delete_custom_backup,
    create_timeshift_snapshot,
    list_timeshift_snapshots,
    restore_timeshift,
    delete_timeshift,
    input_directory_and_backup
)

CUSTOM_BACKUP_DIR = Path("custom_backups")

class RestoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Restore Options")
        self.root.geometry("550x600")

        self.output_box = tk.Text(root, height=30)
        self.output_box.pack(fill=tk.BOTH, expand=True)

        self.input_box = tk.Entry(root)
        self.input_box.pack(fill=tk.X)
        self.input_box.bind("<Return>", self.handle_input)

        self.print_instructions()

    def print_instructions(self):
        instructions = (
            "==== 복원 기능 선택 ===="
            "\n1. 사용자 정의 백업 생성"
            "\n2. 사용자 정의 백업 디렉토리 생성"
            "\n3. 사용자 정의 백업 목록 확인"
            "\n4. 사용자 정의 백업 복원"
            "\n5. 사용자 정의 백업 삭제"
            "\n6. Timeshift 스냅샷 생성"
            "\n7. Timeshift 스냅샷 목록 확인"
            "\n8. Timeshift 복원 (수동)"
            "\n9. Timeshift 삭제 (수동)"
        )
        self.output_box.insert(tk.END, instructions + "\n\n")

    def handle_input(self, event):
        choice = self.input_box.get().strip()
        self.input_box.delete(0, tk.END)

        if choice == "1":
            result = custom_backup()
        elif choice == "2":
            result = input_directory_and_backup()
        elif choice == "3":
            backups = list_custom_backups()
            if backups:
                result = "\n".join(f"- {f.name}" for f in backups)
            else:
                result = "❌ 사용자 정의 백업 없음"
        elif choice == "4":
            file = filedialog.askopenfilename(initialdir=str(CUSTOM_BACKUP_DIR), title="복원할 백업 파일 선택")
            if file:
                dest = filedialog.askdirectory(title="복원할 위치 선택")
                result = "✅ 복원 완료" if restore_custom_backup(Path(file), dest) else "❌ 복원 실패"
            else:
                result = "복원 취소됨."
        elif choice == "5":
            file = filedialog.askopenfilename(initialdir=str(CUSTOM_BACKUP_DIR), title="삭제할 백업 파일 선택")
            if file:
                result = "✅ 삭제 완료" if delete_custom_backup(Path(file)) else "❌ 삭제 실패"
            else:
                result = "삭제 취소됨."
        elif choice == "6":
            result = create_timeshift_snapshot()
        elif choice == "7":
            result = list_timeshift_snapshots()
        elif choice == "8":
            result = restore_timeshift()
        elif choice == "9":
            result = delete_timeshift()
        else:
            result = "❌ 잘못된 선택"

        self.output_box.insert(tk.END, f"\n[결과]\n{result}\n\n")
        self.output_box.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = RestoreGUI(root)
    root.mainloop()
