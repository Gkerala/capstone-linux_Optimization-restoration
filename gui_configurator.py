import tkinter as tk
from tkinter import ttk, messagebox
import json, os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "optimizer_settings.json")

class ConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Optimizer Settings")
        self.entries = {}

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.load_config()
        self.create_tabs()

        save_btn = tk.Button(self.root, text="💾 Save Changes", command=self.save_config)
        save_btn.pack(pady=10)

    def load_config(self):
        try:
            with open(CONFIG_PATH, 'r') as f:
                self.config_data = json.load(f)
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load settings: {e}")
            self.config_data = {}

    def create_tabs(self):
        for section, settings in self.config_data.items():
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=section.replace("_", " ").title())
            self.build_form(tab, settings, parent_key=section)

    def build_form(self, parent, data, parent_key=""):
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                frame = ttk.LabelFrame(parent, text=key.replace("_", " ").title())
                frame.pack(fill="x", padx=10, pady=5, anchor="w")
                self.build_form(frame, value, full_key)
        elif isinstance(data, list):
            self.build_list_editor(parent, data, parent_key)
        else:
            self.build_entry(parent, data, parent_key)

    def build_entry(self, parent, value, key):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=10, pady=2)
        label = ttk.Label(row, text=key.split(".")[-1])
        label.pack(side="left")
        var = tk.StringVar(value=str(value))
        entry = ttk.Entry(row, textvariable=var, width=50)
        entry.pack(side="right", expand=True, fill="x")
        self.entries[key] = var

    def build_list_editor(self, parent, values, key):
        frame = ttk.LabelFrame(parent, text=key.split(".")[-1].replace("_", " ").title())
        frame.pack(fill="x", padx=10, pady=5)

        listbox = tk.Listbox(frame, height=5)
        for v in values:
            listbox.insert("end", v)
        listbox.pack(fill="x", padx=5, pady=2)

        entry_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=entry_var)
        entry.pack(padx=5, pady=2)

        def add_item():
            item = entry_var.get()
            if item:
                listbox.insert("end", item)
                entry_var.set("")

        def remove_item():
            try:
                selected = listbox.curselection()
                listbox.delete(selected)
            except:
                pass

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=2)
        ttk.Button(btn_frame, text="Add", command=add_item).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Remove", command=remove_item).pack(side="left", padx=2)

        self.entries[key] = listbox

    def save_config(self):
        new_config = self.rebuild_config(self.config_data, "")
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(new_config, f, indent=4)
            messagebox.showinfo("Success", "Settings saved.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save: {e}")

    def rebuild_config(self, data, parent_key):
        if isinstance(data, dict):
            return {k: self.rebuild_config(v, f"{parent_key}.{k}" if parent_key else k) for k, v in data.items()}
        elif isinstance(data, list):
            widget = self.entries.get(parent_key)
            if widget:
                return list(widget.get(0, "end"))
            return data
        else:
            widget = self.entries.get(parent_key)
            if widget:
                val = widget.get()
                if val.lower() in ("true", "false"):
                    return val.lower() == "true"
                elif val.isdigit():
                    return int(val)
                return val
            return data


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigApp(root)
    root.mainloop()

