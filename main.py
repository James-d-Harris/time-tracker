import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import json
import os

DATA_FILE = "time_log.json"

class TimeTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker")

        self.current_entry = None

        # ===== TASK INPUT =====
        tk.Label(root, text="Task:").pack()
        self.task_entry = tk.Entry(root, width=40)
        self.task_entry.pack()

        tk.Button(root, text="Add Task", command=self.add_task).pack(pady=5)

        # ===== CLOCK BUTTON =====
        self.clock_btn = tk.Button(root, text="Clock In", command=self.toggle_clock)
        self.clock_btn.pack(pady=10)

        self.status_label = tk.Label(root, text="Status: Clocked Out")
        self.status_label.pack()


        self.start_time = datetime.now()
        messagebox.showinfo("Clock In", f"Started at {self.start_time}")


    # ===== CLOCK LOGIC =====
    def toggle_clock(self):
        if self.current_entry is None:
            self.clock_in()
        else:
            self.clock_out()

    def clock_in(self):
        self.current_entry = {
            "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end": None,
            "tasks": []
        }

        self.clock_btn.config(text="Clock Out")
        self.status_label.config(text="Status: Clocked In")

    def clock_out(self):
        self.current_entry["end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.save_entry(self.current_entry)

        self.current_entry = None
        self.clock_btn.config(text="Clock In")
        self.status_label.config(text="Status: Clocked Out")

        self.refresh_view()

    # ===== TASKS =====
    def add_task(self):
        task = self.task_entry.get().strip()

        if not task:
            messagebox.showwarning("Warning", "Enter a task!")
            return

        if self.current_entry is None:
            messagebox.showwarning("Warning", "Clock in first!")
            return

        self.current_entry["tasks"].append(task)
        self.task_entry.delete(0, tk.END)

    # ===== DATA =====
    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return []

        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []

    def save_entry(self, entry):
        data = self.load_data()
        data.append(entry)

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTracker(root)
    root.mainloop()