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

        self.tree = ttk.Treeview(master)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.build_tree()

        self.update_button = tk.Button(master, text="Update Selected", command=self.update_selected)
        self.update_button.pack(fill=tk.X)

        self.save_button = tk.Button(master, text="Save Config", command=self.save_config)
        self.save_button.pack(fill=tk.X)

    def load_config(self):
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
            self.master.destroy()

    def build_tree(self):
        def insert_items(parent, d):
            for key, value in d.items():
                item_id = self.tree.insert(parent, "end", text=key, values=(value,))
                if isinstance(value, dict):
                    insert_items(item_id, value)

        self.tree.heading("#0", text="Setting")
        self.tree["columns"] = ("Value",)
        self.tree.column("Value", anchor="w")
        self.tree.heading("Value", text="Value")
        insert_items("", self.config)

    def update_selected(self):
        selected = self.tree.focus()
        if not selected:
            return

        key_path = []
        node = selected
        while node:
            key_path.insert(0, self.tree.item(node)["text"])
            node = self.tree.parent(node)

        current_value = self.tree.item(selected)["values"][0]
        if isinstance(current_value, dict):
            messagebox.showinfo("Info", "Can't edit complex structures directly.")
            return

        new_value = simpledialog.askstring("Update", f"Enter new value for {'/'.join(key_path)}:", initialvalue=str(current_value))
        if new_value is None:
            return

        try:
            parsed_value = json.loads(new_value)  # Handles strings, numbers, booleans, null
        except json.JSONDecodeError:
            parsed_value = new_value  # treat as raw string

        # Apply value to dict
        ref = self.config
        for key in key_path[:-1]:
            ref = ref[key]
        ref[key_path[-1]] = parsed_value

        self.tree.item(selected, values=(parsed_value,))
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
    app = SettingEditor(root)
    root.mainloop()
