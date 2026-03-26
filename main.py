import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os

DATA_FILE = "time_log.json"

class TimeTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker")

        self.start_time = None

        self.label = tk.Label(root, text="Task:")
        self.label.pack()

        self.task_entry = tk.Entry(root, width=40)
        self.task_entry.pack()

        self.clock_in_btn = tk.Button(root, text="Clock In", command=self.clock_in)
        self.clock_in_btn.pack(pady=5)

        self.clock_out_btn = tk.Button(root, text="Clock Out", command=self.clock_out)
        self.clock_out_btn.pack(pady=5)

    def clock_in(self):
        if self.start_time is not None:
            messagebox.showwarning("Warning", "Already clocked in!")
            return

        task = self.task_entry.get()
        if not task:
            messagebox.showwarning("Warning", "Enter a task first!")
            return

        self.start_time = datetime.now()
        messagebox.showinfo("Clock In", f"Started at {self.start_time}")

    def clock_out(self):
        if self.start_time is None:
            messagebox.showwarning("Warning", "You are not clocked in!")
            return

        end_time = datetime.now()
        task = self.task_entry.get()

        entry = {
            "start": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "task": task
        }

        self.save_entry(entry)

        self.start_time = None
        self.task_entry.delete(0, tk.END)

        messagebox.showinfo("Clock Out", f"Saved entry:\n{entry}")

    def save_entry(self, entry):
        data = []

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                try:
                    data = json.load(f)
                except:
                    data = []

        data.append(entry)

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTracker(root)
    root.mainloop()