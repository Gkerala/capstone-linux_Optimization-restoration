import tkinter as tk
from tkinter import messagebox, simpledialog
from restore import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    backup_custom,
    list_custom_backups,
    create_timeshift_snapshot,
    list_timeshift_snapshots
)

class RestoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Restore Manager")
        self.root.geometry("400x400")

        tk.Button(root, text="📸 설정 기반 스냅샷 생성", height=2, command=self.create_snapshot).pack(fill=tk.X, pady=5)
        tk.Button(root, text="🗂️ 스냅샷 목록 확인", height=2, command=self.list_snapshots).pack(fill=tk.X, pady=5)
        tk.Button(root, text="♻️ 스냅샷 복원", height=2, command=self.restore_snapshot).pack(fill=tk.X, pady=5)
        tk.Button(root, text="🧾 사용자 정의 백업", height=2, command=self.backup_custom).pack(fill=tk.X, pady=5)
        tk.Button(root, text="📁 사용자 정의 백업 목록", height=2, command=self.list_custom_backups).pack(fill=tk.X, pady=5)
        tk.Button(root, text="🧬 Timeshift 스냅샷 생성", height=2, command=self.create_timeshift_snapshot).pack(fill=tk.X, pady=5)
        tk.Button(root, text="📜 Timeshift 스냅샷 목록", height=2, command=self.list_timeshift_snapshots).pack(fill=tk.X, pady=5)

    def create_snapshot(self):
        path = create_snapshot()
        messagebox.showinfo("완료", f"스냅샷 생성 완료: {path}")

    def list_snapshots(self):
        snapshots = list_snapshots()
        messagebox.showinfo("스냅샷 목록", "\n".join([s.name for s in snapshots]))

    def restore_snapshot(self):
        snapshot_name = simpledialog.askstring("복원", "복원할 스냅샷 이름:")
        if snapshot_name:
            restore_snapshot(snapshot_name)
            messagebox.showinfo("완료", f"복원 완료: {snapshot_name}")

    def backup_custom(self):
        path = backup_custom()
        messagebox.showinfo("완료", f"사용자 정의 백업 완료: {path}")

    def list_custom_backups(self):
        entries = list_custom_backups()
        messagebox.showinfo("백업 목록", "\n".join([e.name for e in entries]))

    def create_timeshift_snapshot(self):
        create_timeshift_snapshot()
        messagebox.showinfo("완료", "Timeshift 스냅샷 생성 완료")

    def list_timeshift_snapshots(self):
        snapshots = list_timeshift_snapshots()
        messagebox.showinfo("Timeshift 목록", snapshots)

if __name__ == "__main__":
    root = tk.Tk()
    app = RestoreGUI(root)
    root.mainloop()
