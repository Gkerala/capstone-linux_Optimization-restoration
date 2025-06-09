import tkinter as tk
from tkinter import ttk
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.gui.sections.optimize_tab import create_optimize_tab
from src.gui.sections.restore_tab import create_restore_tab
from src.gui.sections.settings_tab import create_settings_tab


def main():
    root = tk.Tk()
    root.title("Linux Optimizer & Restore")
    root.geometry("900x600")

    # 왼쪽 사이드 네비게이션 영역
    sidebar = tk.Frame(root, width=150, bg="#2c3e50")
    sidebar.pack(side="left", fill="y")

    # 메인 컨텐츠 영역
    content_frame = tk.Frame(root)
    content_frame.pack(side="right", fill="both", expand=True)

    # 탭 컨트롤러 (내용을 동적으로 교체)
    notebook = ttk.Notebook(content_frame)
    notebook.pack(fill="both", expand=True)

    # 탭들 생성
    optimize_tab = create_optimize_tab(notebook)
    restore_tab = create_restore_tab(notebook)
    settings_tab = create_settings_tab(notebook)

    notebook.add(optimize_tab, text="최적화")
    notebook.add(restore_tab, text="복원")
    notebook.add(settings_tab, text="설정")

    # 사이드바 버튼 함수
    def switch_tab(index):
        notebook.select(index)

    # 사이드바 버튼들
    tk.Button(sidebar, text="최적화", command=lambda: switch_tab(0), width=20, height=3, bg="#34495e", fg="white").pack(pady=5)
    tk.Button(sidebar, text="복원", command=lambda: switch_tab(1), width=20, height=3, bg="#34495e", fg="white").pack(pady=5)
    tk.Button(sidebar, text="설정", command=lambda: switch_tab(2), width=20, height=3, bg="#34495e", fg="white").pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
