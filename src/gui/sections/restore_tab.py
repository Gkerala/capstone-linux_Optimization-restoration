import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from src.restore import (
    custom_backup,
    custom_directory_backup,
    list_custom_backups,
    restore_custom_backup,
    delete_custom_backup
)

CUSTOM_BACKUP_DIR = Path("custom_backups")

def create_restore_tab(notebook):
    frame = tk.Frame(notebook)

    # 백업 리스트
    backup_listbox = tk.Listbox(frame, width=60)
    backup_listbox.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

    # 복원 위치 선택용
    restore_dir_var = tk.StringVar()
    restore_entry = tk.Entry(frame, textvariable=restore_dir_var, width=45)
    restore_entry.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="w")

    def select_restore_path():
        path = filedialog.askdirectory(title="복원할 위치 선택")
        if path:
            restore_dir_var.set(path)

    tk.Button(frame, text="경로 선택", command=select_restore_path).grid(row=1, column=1, pady=5, sticky="w")

    # 결과 출력
    result_label = tk.Label(frame, text="", fg="blue")
    result_label.grid(row=5, column=0, columnspan=3, pady=10)

    def refresh_list():
        backup_listbox.delete(0, tk.END)
        backups = list_custom_backups()
        for file in backups:
            backup_listbox.insert(tk.END, file.name)

    def handle_custom_backup():
        result = custom_backup()
        result_label.config(text=result)
        refresh_list()

    def handle_custom_directory_backup():
        result = custom_directory_backup()
        result_label.config(text=result)
        refresh_list()

    def handle_restore():
        selection = backup_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "복원할 파일을 선택하세요.")
            return
        file_name = backup_listbox.get(selection[0])
        file_path = CUSTOM_BACKUP_DIR / file_name
        dest = restore_dir_var.get()

        if not dest or not Path(dest).exists():
            messagebox.showwarning("경고", "복원할 경로를 올바르게 지정하세요.")
            return

        success = restore_custom_backup(file_path, dest)
        result_label.config(text="✅ 복원 성공" if success else "❌ 복원 실패")

    def handle_delete():
        selection = backup_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 백업을 선택하세요.")
            return
        file_name = backup_listbox.get(selection[0])
        file_path = CUSTOM_BACKUP_DIR / file_name
        if delete_custom_backup(file_path):
            result_label.config(text=f"✅ 삭제 완료: {file_name}")
            refresh_list()
        else:
            result_label.config(text=f"❌ 삭제 실패: {file_name}")

    # 버튼들
    tk.Button(frame, text="파일 백업", command=handle_custom_backup).grid(row=2, column=0, pady=5, sticky="w", padx=10)
    tk.Button(frame, text="디렉토리 백업", command=handle_custom_directory_backup).grid(row=2, column=1, pady=5, sticky="w")
    tk.Button(frame, text="복원", command=handle_restore).grid(row=3, column=0, pady=5, sticky="w", padx=10)
    tk.Button(frame, text="삭제", command=handle_delete).grid(row=3, column=1, pady=5, sticky="w")

    refresh_list()
    return frame
