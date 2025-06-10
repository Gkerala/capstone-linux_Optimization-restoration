import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from src.utils.logger import get_logger
from src.restore import (
    custom_backup,
    custom_directory_backup,
    list_custom_backups,
    restore_custom_backup,
    delete_custom_backup
)

logger = get_logger(__name__)
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
            logger.info(f"📂 복원 경로 선택됨: {path}")

    tk.Button(frame, text="📂 경로 선택", command=select_restore_path).grid(row=1, column=1, pady=5, sticky="w")

    # 결과 출력
    result_label = tk.Label(frame, text="", fg="blue")
    result_label.grid(row=5, column=0, columnspan=3, pady=10)

    def refresh_list():
        backup_listbox.delete(0, tk.END)
        backups = list_custom_backups()
        for file in backups:
            backup_listbox.insert(tk.END, file.name)
        logger.info(f"📦 백업 목록 갱신됨 ({len(backups)}개)")

    def handle_custom_backup():
        result = custom_backup()
        result_label.config(text=result)
        logger.info(result)
        refresh_list()

    def handle_custom_directory_backup():
        result = custom_directory_backup()
        result_label.config(text=result)
        logger.info(result)
        refresh_list()

    def handle_restore():
        selection = backup_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "복원할 파일을 선택하세요.")
            logger.warning("❗ 복원할 파일이 선택되지 않음")
            return

        file_name = backup_listbox.get(selection[0])
        file_path = CUSTOM_BACKUP_DIR / file_name
        dest = restore_dir_var.get()

        if not dest or not Path(dest).exists():
            messagebox.showwarning("경고", "복원할 경로를 올바르게 지정하세요.")
            logger.warning("❗ 복원 경로가 유효하지 않음")
            return

        success = restore_custom_backup(file_path, dest)
        msg = "✅ 복원 성공" if success else "❌ 복원 실패"
        result_label.config(text=msg)
        logger.info(f"{msg}: {file_name} -> {dest}")

    def handle_delete():
        selection = backup_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 백업을 선택하세요.")
            logger.warning("❗ 삭제할 항목이 선택되지 않음")
            return

        file_name = backup_listbox.get(selection[0])
        file_path = CUSTOM_BACKUP_DIR / file_name

        if delete_custom_backup(file_path):
            msg = f"✅ 삭제 완료: {file_name}"
            result_label.config(text=msg)
            logger.info(msg)
            refresh_list()
        else:
            msg = f"❌ 삭제 실패: {file_name}"
            result_label.config(text=msg)
            logger.error(msg)

    # 버튼들
    tk.Button(frame, text="파일 백업", command=handle_custom_backup).grid(row=2, column=0, pady=5, sticky="w", padx=10)
    tk.Button(frame, text="디렉토리 백업", command=handle_custom_directory_backup).grid(row=2, column=1, pady=5, sticky="w")
    tk.Button(frame, text="복원", command=handle_restore).grid(row=3, column=0, pady=5, sticky="w", padx=10)
    tk.Button(frame, text="삭제", command=handle_delete).grid(row=3, column=1, pady=5, sticky="w")

    refresh_list()
    return frame
