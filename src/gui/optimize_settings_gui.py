import json
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from pathlib import Path

CONFIG_PATH = Path("config/optimizer_settings.json")

class SettingEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Setting Editor")
        self.config = self.load_config()

        self.tab_control = ttk.Notebook(master)
        self.tab_control.pack(fill=tk.BOTH, expand=True)

        self.treeviews = {}
        self.tabs = {}

        # 설정의 최상위 항목별로 탭 생성
        for section in self.config:
            tab = ttk.Frame(self.tab_control)
            self.tab_control.add(tab, text=section)
            self.tabs[section] = tab

            tree = ttk.Treeview(tab)
            tree.pack(fill=tk.BOTH, expand=True)
            self.treeviews[section] = tree
            self.build_tree(tree, self.config[section])

        # 하단 버튼
        btn_frame = tk.Frame(master)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Update Selected", command=self.update_selected).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Save Config", command=self.save_config).pack(side=tk.LEFT)

    def load_config(self):
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
            self.master.destroy()
            return {}

    def build_tree(self, tree, data):
        def insert_items(parent, d):
            for key, value in d.items():
                item_id = tree.insert(parent, "end", text=key, values=(value,))
                if isinstance(value, dict):
                    insert_items(item_id, value)

        tree.heading("#0", text="Setting")
        tree["columns"] = ("Value",)
        tree.column("Value", anchor="w", width=300)
        tree.heading("Value", text="Value")
        insert_items("", data)

    def update_selected(self):
        current_tab = self.tab_control.select()
        current_tab_name = self.tab_control.tab(current_tab, "text")
        tree = self.treeviews[current_tab_name]

        selected = tree.focus()
        if not selected:
            return

        key_path = []
        node = selected
        while node:
            key_path.insert(0, tree.item(node)["text"])
            node = tree.parent(node)

        current_value = tree.item(selected)["values"][0]
        if isinstance(current_value, dict):
            messagebox.showinfo("Info", "Can't edit complex structures directly.")
            return

        new_value = simpledialog.askstring("Update", f"Enter new value for {'/'.join(key_path)}:", initialvalue=str(current_value))
        if new_value is None:
            return

        try:
            parsed_value = json.loads(new_value)
        except json.JSONDecodeError:
            parsed_value = new_value

        ref = self.config[current_tab_name]
        for key in key_path[:-1]:
            ref = ref[key]
        ref[key_path[-1]] = parsed_value

        tree.item(selected, values=(parsed_value,))
        messagebox.showinfo("Pending Save", "Value updated. Click 'Save Config' to apply changes.")

    def save_config(self):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(self.config, f, indent=4)
            messagebox.showinfo("Success", "Configuration successfully saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x600")
    app = SettingEditor(root)
    root.mainloop()
