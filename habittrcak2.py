
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import date, timedelta

# ---------------- CONFIGURATION ----------------

FILE_NAME = "habit_data.json"
TODAY = date.today().isoformat()

BG = "#F3F6FB"
CARD = "#FFFFFF"
PRIMARY = "#4F46E5"
GREEN = "#16A34A"
RED = "#DC2626"
TEXT = "#172033"
MUTED = "#64748B"

# ---------------- DATA MANAGEMENT ----------------

def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, OSError):
            messagebox.showwarning(
                "Data warning",
                "Could not read saved data. Starting with an empty tracker."
            )
    return []


habits = load_data()


def save_data():
    try:
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            json.dump(habits, file, indent=4)
    except OSError as error:
        messagebox.showerror("Save error", str(error))


def is_completed(habit, day):
    return day in habit.get("completed_dates", [])


def current_streak(habit):
    completed = set(habit.get("completed_dates", []))
    day = date.today()

    # If today is incomplete, check whether yesterday
    # was the last completed day.
    if day.isoformat() not in completed:
        day -= timedelta(days=1)

    streak = 0
    while day.isoformat() in completed:
        streak += 1
        day -= timedelta(days=1)

    return streak


def longest_streak(habit):
    dates = sorted(set(habit.get("completed_dates", [])))
    if not dates:
        return 0

    longest = 1
    streak = 1

    for i in range(1, len(dates)):
        previous = date.fromisoformat(dates[i - 1])
        current = date.fromisoformat(dates[i])

        if current == previous + timedelta(days=1):
            streak += 1
        else:
            streak = 1

        longest = max(longest, streak)

    return longest


def weekly_count(habit):
    completed = set(habit.get("completed_dates", []))
    start = date.today() - timedelta(days=6)

    return sum(
        1 for i in range(7)
        if (start + timedelta(days=i)).isoformat() in completed
    )


def total_completed_days():
    return sum(len(set(h.get("completed_dates", []))) for h in habits)


def today_progress():
    total = len(habits)
    completed = sum(is_completed(h, TODAY) for h in habits)
    percent = round(completed / total * 100) if total else 0
    return completed, total, percent


# ---------------- WINDOW ----------------

root = tk.Tk()
root.title("HabitFlow | Personal Habit Tracker")
root.geometry("1050x720")
root.minsize(850, 600)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox", padding=5)

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=25, pady=(20, 10))

tk.Label(
    header,
    text="HabitFlow",
    font=("Arial", 25, "bold"),
    bg=BG,
    fg=PRIMARY
).pack(side="left")

tk.Label(
    header,
    text="Build better habits. Track your growth.",
    font=("Arial", 11),
    bg=BG,
    fg=MUTED
).pack(side="left", padx=18, pady=8)

date_label = tk.Label(
    root,
    text=date.today().strftime("%A, %d %B %Y"),
    font=("Arial", 11),
    bg=BG,
    fg=MUTED
)
date_label.pack(anchor="w", padx=28)

nav = tk.Frame(root, bg=BG)
nav.pack(fill="x", padx=25, pady=15)

content = tk.Frame(root, bg=BG)
content.pack(fill="both", expand=True, padx=25, pady=(0, 20))


def clear_content():
    for widget in content.winfo_children():
        widget.destroy()


def make_card(parent, title, value, subtitle):
    card = tk.Frame(
        parent, bg=CARD, padx=16, pady=15,
        highlightbackground="#E2E8F0",
        highlightthickness=1
    )

    tk.Label(
        card, text=title, font=("Arial", 10),
        bg=CARD, fg=MUTED
    ).pack(anchor="w")

    tk.Label(
        card, text=value, font=("Arial", 23, "bold"),
        bg=CARD, fg=PRIMARY
    ).pack(anchor="w", pady=5)

    tk.Label(
        card, text=subtitle, font=("Arial", 9),
        bg=CARD, fg=MUTED
    ).pack(anchor="w")

    return card


def heading(parent, title, subtitle=""):
    tk.Label(
        parent, text=title, font=("Arial", 19, "bold"),
        bg=BG, fg=TEXT
    ).pack(anchor="w", pady=(0, 5))

    if subtitle:
        tk.Label(
            parent, text=subtitle, font=("Arial", 10),
            bg=BG, fg=MUTED
        ).pack(anchor="w", pady=(0, 15))


def action_button(parent, text, command, color=PRIMARY):
    return tk.Button(
        parent, text=text, command=command,
        bg=color, fg="white", activebackground=color,
        activeforeground="white", relief="flat",
        cursor="hand2", font=("Arial", 10, "bold"),
        padx=12, pady=7
    )


# ---------------- DASHBOARD ----------------

def show_dashboard():
    clear_content()
    heading(content, "Your Dashboard",
            "A quick look at your daily habits and consistency.")

    completed, total, percent = today_progress()

    cards = tk.Frame(content, bg=BG)
    cards.pack(fill="x", pady=8)

    make_card(
        cards, "TODAY'S PROGRESS",
        f"{percent}%", f"{completed} of {total} habits completed"
    ).pack(side="left", fill="x", expand=True, padx=(0, 8))

    make_card(
        cards, "TOTAL HABITS", str(total),
        "Habits you are currently tracking"
    ).pack(side="left", fill="x", expand=True, padx=8)

    make_card(
        cards, "COMPLETED DAYS",
        str(total_completed_days()),
        "Total habit completions recorded"
    ).pack(side="left", fill="x", expand=True, padx=(8, 0))

    progress_box = tk.Frame(
        content, bg=CARD, padx=15, pady=12
    )
    progress_box.pack(fill="x", pady=12)

    tk.Label(
        progress_box, text="Daily completion",
        font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
    ).pack(anchor="w")

    bar = ttk.Progressbar(
        progress_box, maximum=100, value=percent, length=500
    )
    bar.pack(fill="x", pady=10)

    tk.Label(
        progress_box,
        text=f"{completed}/{total} completed today",
        bg=CARD, fg=MUTED, font=("Arial", 10)
    ).pack(anchor="w")

    tk.Label(
        content, text="Today's Habits",
        font=("Arial", 15, "bold"), bg=BG, fg=TEXT
    ).pack(anchor="w", pady=(12, 8))

    list_box = tk.Frame(content, bg=BG)
    list_box.pack(fill="both", expand=True)

    if not habits:
        tk.Label(
            list_box,
            text="No habits yet. Open Manage Habits to add your first habit!",
            bg=BG, fg=MUTED, font=("Arial", 12)
        ).pack(anchor="w", pady=15)
        return

    for habit in habits:
        row = tk.Frame(
            list_box, bg=CARD, padx=12, pady=9,
            highlightbackground="#E2E8F0",
            highlightthickness=1
        )
        row.pack(fill="x", pady=4)

        done = is_completed(habit, TODAY)

        tk.Label(
            row, text="✓" if done else "○",
            font=("Arial", 19, "bold"),
            fg=GREEN if done else MUTED, bg=CARD
        ).pack(side="left", padx=(0, 12))

        info = tk.Frame(row, bg=CARD)
        info.pack(side="left", fill="x", expand=True)

        tk.Label(
            info, text=habit["name"],
            font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            info,
            text=f"{habit.get('category', 'General')}  |  "
                 f"Streak: {current_streak(habit)} days  |  "
                 f"This week: {weekly_count(habit)}/7",
            font=("Arial", 9), bg=CARD, fg=MUTED
        ).pack(anchor="w", pady=(3, 0))

        action_button(
            row,
            "Undo" if done else "Mark Done",
            lambda h=habit: toggle_completion(h),
            GREEN if not done else MUTED
        ).pack(side="right", padx=5)


def toggle_completion(habit):
    completed_dates = habit.setdefault("completed_dates", [])

    if TODAY in completed_dates:
        completed_dates.remove(TODAY)
    else:
        completed_dates.append(TODAY)

    save_data()
    show_dashboard()


# ---------------- MANAGE HABITS ----------------

def show_manage():
    clear_content()
    heading(content, "Manage Habits",
            "Create habits and organize your personal routine.")

    form = tk.Frame(
        content, bg=CARD, padx=18, pady=15,
        highlightbackground="#E2E8F0",
        highlightthickness=1
    )
    form.pack(fill="x", pady=(0, 15))

    tk.Label(
        form, text="Add a New Habit",
        font=("Arial", 13, "bold"), bg=CARD, fg=TEXT
    ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

    tk.Label(form, text="Habit name", bg=CARD, fg=TEXT).grid(
        row=1, column=0, sticky="w", pady=5
    )
    name_entry = tk.Entry(form, font=("Arial", 11), width=30)
    name_entry.grid(row=1, column=1, sticky="w", pady=5)

    tk.Label(form, text="Category", bg=CARD, fg=TEXT).grid(
        row=2, column=0, sticky="w", pady=5
    )
    category_box = ttk.Combobox(
        form,
        values=[
            "Health", "Fitness", "Study", "Personal Growth",
            "Mindfulness", "Productivity", "Other"
        ],
        state="readonly", width=27
    )
    category_box.set("Personal Growth")
    category_box.grid(row=2, column=1, sticky="w", pady=5)

    tk.Label(form, text="Notes / goal", bg=CARD, fg=TEXT).grid(
        row=3, column=0, sticky="w", pady=5
    )
    note_entry = tk.Entry(form, font=("Arial", 11), width=30)
    note_entry.grid(row=3, column=1, sticky="w", pady=5)

    def add_new():
        name = name_entry.get().strip()
        category = category_box.get()
        note = note_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Missing name", "Please enter a habit name."
            )
            return

        if any(h["name"].lower() == name.lower() for h in habits):
            messagebox.showwarning(
                "Duplicate habit", "This habit already exists."
            )
            return

        habits.append({
            "name": name,
            "category": category,
            "notes": note,
            "completed_dates": []
        })

        save_data()
        show_manage()

    action_button(form, "＋ Add Habit", add_new).grid(
        row=4, column=1, sticky="w", pady=(12, 0)
    )

    tk.Label(
        content, text=f"Your Habits ({len(habits)})",
        font=("Arial", 14, "bold"), bg=BG, fg=TEXT
    ).pack(anchor="w", pady=(5, 10))

    for habit in habits:
        row = tk.Frame(content, bg=CARD, padx=12, pady=10)
        row.pack(fill="x", pady=4)

        info = tk.Frame(row, bg=CARD)
        info.pack(side="left", fill="x", expand=True)

        tk.Label(
            info, text=habit["name"],
            font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            info,
            text=f"{habit.get('category', 'General')}  |  "
                 f"Best streak: {longest_streak(habit)} days",
            bg=CARD, fg=MUTED, font=("Arial", 9)
        ).pack(anchor="w", pady=3)

        if habit.get("notes"):
            tk.Label(
                info, text=f"Goal: {habit['notes']}",
                bg=CARD, fg=MUTED, font=("Arial", 9)
            ).pack(anchor="w")

        action_button(
            row, "Delete",
            lambda h=habit: delete_habit(h), RED
        ).pack(side="right", padx=5)


def delete_habit(habit):
    if messagebox.askyesno(
        "Delete Habit",
        f"Delete '{habit['name']}' and its tracking history?"
    ):
        habits.remove(habit)
        save_data()
        show_manage()


# ---------------- HISTORY ----------------

def show_history():
    clear_content()
    heading(content, "Habit History",
            "Review your records for any date.")

    controls = tk.Frame(content, bg=BG)
    controls.pack(fill="x", pady=10)

    tk.Label(
        controls, text="Date (YYYY-MM-DD):",
        font=("Arial", 10), bg=BG, fg=TEXT
    ).pack(side="left", padx=(0, 8))

    history_entry = tk.Entry(controls, width=14, font=("Arial", 11))
    history_entry.insert(0, TODAY)
    history_entry.pack(side="left", padx=5)

    results = tk.Frame(content, bg=BG)
    results.pack(fill="both", expand=True, pady=10)

    def search_history():
        selected = history_entry.get().strip()

        try:
            date.fromisoformat(selected)
        except ValueError:
            messagebox.showerror(
                "Invalid date", "Use YYYY-MM-DD, for example 2026-10-16."
            )
            return

        for widget in results.winfo_children():
            widget.destroy()

        completed = sum(
            is_completed(h, selected) for h in habits
        )
        total = len(habits)
        percent = round(completed / total * 100) if total else 0

        tk.Label(
            results,
            text=f"Record for {selected}",
            font=("Arial", 15, "bold"), bg=BG, fg=TEXT
        ).pack(anchor="w", pady=5)

        tk.Label(
            results,
            text=f"Completed: {completed}/{total}  |  "
                 f"Daily progress: {percent}%",
            font=("Arial", 11), bg=BG, fg=PRIMARY
        ).pack(anchor="w", pady=(0, 12))

        for habit in habits:
            done = is_completed(habit, selected)
            tk.Label(
                results,
                text=f"{'✓' if done else '○'}  {habit['name']} - "
                     f"{'Completed' if done else 'Not completed'}",
                bg=BG, fg=GREEN if done else MUTED,
                font=("Arial", 11)
            ).pack(anchor="w", pady=5)

    action_button(controls, "View Record", search_history).pack(
        side="left", padx=8
    )
    search_history()


# ---------------- STATISTICS ----------------

def show_statistics():
    clear_content()
    heading(content, "Progress & Statistics",
            "Measure consistency and celebrate your improvement.")

    completed, total, percent = today_progress()

    all_dates = set()
    for habit in habits:
        all_dates.update(habit.get("completed_dates", []))

    cards = tk.Frame(content, bg=BG)
    cards.pack(fill="x", pady=10)

    make_card(
        cards, "TODAY", f"{percent}%",
        f"{completed} of {total} habits"
    ).pack(side="left", fill="x", expand=True, padx=(0, 8))

    make_card(
        cards, "ALL COMPLETIONS",
        str(total_completed_days()), "Habit completion records"
    ).pack(side="left", fill="x", expand=True, padx=8)

    make_card(
        cards, "ACTIVE RECORD DAYS",
        str(len(all_dates)), "Dates with at least one completion"
    ).pack(side="left", fill="x", expand=True, padx=(8, 0))

    tk.Label(
        content, text="Habit Performance",
        font=("Arial", 15, "bold"), bg=BG, fg=TEXT
    ).pack(anchor="w", pady=(18, 10))

    for habit in habits:
        count = len(set(habit.get("completed_dates", [])))
        best = longest_streak(habit)
        current = current_streak(habit)
        week = weekly_count(habit)

        row = tk.Frame(content, bg=CARD, padx=12, pady=10)
        row.pack(fill="x", pady=4)

        tk.Label(
            row, text=habit["name"],
            font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            row,
            text=f"Total completions: {count}   |   "
                 f"Current streak: {current} days   |   "
                 f"Best streak: {best} days   |   "
                 f"Last 7 days: {week}/7",
            font=("Arial", 10), bg=CARD, fg=MUTED
        ).pack(anchor="w", pady=5)

        bar = ttk.Progressbar(
            row, maximum=7, value=week, length=350
        )
        bar.pack(anchor="w", fill="x", pady=3)


# ---------------- NAVIGATION ----------------

def make_nav_button(text, command):
    tk.Button(
        nav, text=text, command=command,
        bg=PRIMARY, fg="white",
        activebackground="#3730A3",
        activeforeground="white",
        relief="flat", cursor="hand2",
        font=("Arial", 10, "bold"),
        padx=13, pady=8
    ).pack(side="left", padx=(0, 8))


make_nav_button("Dashboard", show_dashboard)
make_nav_button("Manage Habits", show_manage)
make_nav_button("History", show_history)
make_nav_button("Statistics", show_statistics)

show_dashboard()
root.mainloop()
