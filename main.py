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

        # ===== VIEW MODE =====
        self.view_mode = tk.StringVar(value="weekly")

        tk.Radiobutton(root, text="Daily", variable=self.view_mode, value="daily", command=self.refresh_view).pack()
        tk.Radiobutton(root, text="Weekly", variable=self.view_mode, value="weekly", command=self.refresh_view).pack()
        tk.Radiobutton(root, text="Monthly", variable=self.view_mode, value="monthly", command=self.refresh_view).pack()

        # ===== CANVAS =====
        self.canvas = tk.Canvas(root, width=900, height=600, bg="white")
        self.canvas.pack()

        self.refresh_view()

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

    # ===== WEEK RANGE =====
    def get_week_range(self):
        now = datetime.now()
        days_until_saturday = (5 - now.weekday()) % 7
        end_of_week = now + timedelta(days=days_until_saturday)
        start_of_week = end_of_week - timedelta(days=6)

        return start_of_week, end_of_week

    # ===== VIEW =====
    def refresh_view(self):
        self.canvas.delete("all")

        data = self.load_data()

        if self.view_mode.get() == "weekly":
            self.draw_weekly_vertical(data)

    # ===== VERTICAL TIMELINE =====
    def draw_weekly_vertical(self, data):
        start_week, _ = self.get_week_range()

        # Layout
        canvas_width = 900
        canvas_height = 600

        top_margin = 60
        bottom_margin = 20
        left_margin = 70
        right_margin = 20

        timeline_height = canvas_height - top_margin - bottom_margin
        timeline_width = canvas_width - left_margin - right_margin

        day_width = timeline_width / 7

        # ===== DRAW DAY COLUMNS + HEADERS =====
        header_height = 40

        for i in range(7):
            x1 = left_margin + i * day_width
            x2 = x1 + day_width

            day = start_week + timedelta(days=i)

            # Column background (timeline area)
            fill_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"

            self.canvas.create_rectangle(
                x1, top_margin,
                x2, top_margin + timeline_height,
                fill=fill_color,
                outline="#cccccc"
            )

            # Header background
            self.canvas.create_rectangle(
                x1, top_margin - header_height,
                x2, top_margin,
                fill="#eaeaea",
                outline="#cccccc"
            )

            # Day name (bigger, bold)
            self.canvas.create_text(
                (x1 + x2) / 2,
                top_margin - 25,
                text=day.strftime("%A"),
                font=("Arial", 11, "bold"),
                fill="black"
            )

            # Date (smaller)
            self.canvas.create_text(
                (x1 + x2) / 2,
                top_margin - 10,
                text=day.strftime("%b %d, %Y"),
                font=("Arial", 9),
                fill="black"
            )

        # ===== DRAW HOUR GRID =====
        for h in range(25):
            y = top_margin + (h / 24) * timeline_height

            # Grid line every hour
            self.canvas.create_line(
                left_margin,
                y,
                left_margin + timeline_width,
                y,
                fill=h%2==1 and "#e0e0e0" or "#3f3f3f"
            )

            # Label every 2 hours
            if h % 2 == 0:
                self.canvas.create_text(
                    left_margin - 10,
                    y,
                    text=f"{h:02d}:00",
                    font=("Arial", 9),
                    fill="black",
                    anchor="e"  # right-aligns text nicely
                )

        
        # ===== DRAW TIME BLOCKS =====
        for entry in data:
            start = datetime.strptime(entry["start"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(entry["end"], "%Y-%m-%d %H:%M:%S")

            day_index = (start.date() - start_week.date()).days

            if day_index < 0 or day_index > 6:
                continue

            x1 = left_margin + day_index * day_width
            x2 = x1 + day_width

            # Convert time → vertical position
            start_hour = start.hour + start.minute / 60
            end_hour = end.hour + end.minute / 60

            y1 = top_margin + (start_hour / 24) * timeline_height
            y2 = top_margin + (end_hour / 24) * timeline_height

            # Draw block with padding inside column
            self.canvas.create_rectangle(
                x1 + 8,
                y1,
                x2 - 8,
                y2,
                fill="#4CAF50",
                outline=""
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTracker(root)
    root.mainloop()