import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sv_ttk
import darkdetect

DEFAULT_EXTENSIONS = ['.java', '.cpp', '.c', '.h', '.py', '.js', '.ts', '.tsx',
                      '.html', '.css', '.txt', '.md', '.json', '.xml', '.cs']

class LineCounterApp:
    def __init__(self, master):
        self.master = master
        master.title("CNLineCounter")
        master.resizable(False, False)

        self.selected_extensions = {ext: tk.BooleanVar(value=True) for ext in DEFAULT_EXTENSIONS}

        # Root container
        root_frame = ttk.Frame(master, padding=10)
        root_frame.grid(row=0, column=0, sticky="nsew")

        # Left panel for main controls
        left_panel = ttk.Frame(root_frame, padding=10)
        left_panel.grid(row=0, column=0, sticky="n")

        self.path_var = tk.StringVar()
        self.result_var = tk.StringVar()

        ttk.Label(left_panel, text="Selected Directory:").grid(row=0, column=0, sticky="w")
        self.entry = ttk.Entry(left_panel, textvariable=self.path_var, width=50)
        self.entry.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")

        self.browse_button = ttk.Button(left_panel, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=1, column=2, padx=(10, 0))

        self.run_button = ttk.Button(left_panel, text="Run", command=self.run_line_count)
        self.run_button.grid(row=2, column=0, pady=20, sticky="w", columnspan=3)

        ttk.Label(left_panel, text="Total Lines:").grid(row=3, column=0, sticky="w")
        self.result_entry = ttk.Entry(left_panel, textvariable=self.result_var, width=20, state='readonly')
        self.result_entry.grid(row=4, column=0, sticky="w", pady=5)

        # Right panel for extension filters
        right_panel = ttk.LabelFrame(root_frame, text="File Types", padding=10)
        right_panel.grid(row=0, column=1, padx=(20, 0), sticky="ns")

        self.filter_canvas = tk.Canvas(right_panel, width=100, height=300)
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.filter_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.filter_canvas)

        self.filter_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.filter_canvas.configure(yscrollcommand=scrollbar.set)
        self.filter_canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.filter_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        self.scrollable_frame.bind("<Configure>", lambda e: self.filter_canvas.configure(scrollregion=self.filter_canvas.bbox("all")))

        self.filter_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.select_all_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.scrollable_frame, text="Select All", variable=self.select_all_var, command=self.toggle_all_extensions).pack(anchor="w", pady=(0, 5))

        for ext, var in self.selected_extensions.items():
            ttk.Checkbutton(self.scrollable_frame, text=ext, variable=var).pack(anchor="w")

    def _bind_mousewheel(self):
        self.master.bind_all("<MouseWheel>", self._on_mousewheel)
        self.master.bind_all("<Button-4>", self._on_mousewheel)  # Linux
        self.master.bind_all("<Button-5>", self._on_mousewheel)  # Linux

    def _unbind_mousewheel(self):
        self.master.unbind_all("<MouseWheel>")
        self.master.unbind_all("<Button-4>")
        self.master.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:  # Linux scroll up
            self.filter_canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.filter_canvas.yview_scroll(1, "units")
        else:  # Windows and macOS
            self.filter_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def toggle_all_extensions(self):
        state = self.select_all_var.get()
        for var in self.selected_extensions.values():
            var.set(state)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)

    def run_line_count(self):
        directory = self.path_var.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Invalid directory selected.")
            return

        selected_exts = {ext for ext, var in self.selected_extensions.items() if var.get()}
        total_lines = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in selected_exts):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            total_lines += sum(1 for _ in f)
                    except Exception as e:
                        print(f"Error reading {file}: {e}")

        self.result_var.set(str(total_lines))

if __name__ == "__main__":
    root = tk.Tk()
    sv_ttk.set_theme(darkdetect.theme())
    app = LineCounterApp(root)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')

    root.mainloop()
