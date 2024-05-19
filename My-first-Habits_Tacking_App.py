import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime

# Database connection
conn = sqlite3.connect("habits.db")
habit_ids = []


def create_table():
    global conn
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        frequency TEXT,
                        goal TEXT,
                        duration TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS completions (
                        id INTEGER PRIMARY KEY,
                        habit_id INTEGER,
                        date TEXT,
                        UNIQUE(habit_id, date),
                        FOREIGN KEY (habit_id) REFERENCES habits(id)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
                        id INTEGER PRIMARY KEY,
                        habit_id INTEGER,
                        reminder_date TEXT,
                        FOREIGN KEY (habit_id) REFERENCES habits(id)
                    )''')
    conn.commit()


def create_habit():
    name = habit_name_entry.get()
    if not name:
        messagebox.showerror("Error", "Please enter a name for the habit.")
        return

    frequency = habit_frequency_combobox.get()
    goal = habit_goal_entry.get()
    duration = f"{hours_spinbox.get()} hours and {minutes_spinbox.get()} minutes"

    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (name, frequency, goal, duration) VALUES (?, ?, ?, ?)",
                   (name, frequency, goal, duration))
    conn.commit()
    messagebox.showinfo("Success", "Habit created successfully.")
    refresh_habits_listbox()


def track_habit():
    selected_item = habits_listbox.curselection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a habit to track.")
        return
    idx = selected_item[0]
    habit_id_selected = habit_ids[idx]

    # Check if habit is already tracked today
    today = datetime.today().strftime("%Y-%m-%d")
    cursor_track = conn.cursor()
    cursor_track.execute("SELECT COUNT(*) FROM completions WHERE habit_id=? AND date=?", (habit_id_selected, today))
    if cursor_track.fetchone()[0] > 0:
        messagebox.showinfo("Info", "You've already tracked this habit today.")
        return

    cursor_track.execute("INSERT INTO completions (habit_id, date) VALUES (?, ?)", (habit_id_selected, today))
    conn.commit()
    messagebox.showinfo("Success", "Habit tracked for today!")
    refresh_habits_listbox()


def delete_habit():
    selected_item = habits_listbox.curselection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a habit to delete.")
        return
    idx_delete = selected_item[0]
    habit_id_delete = habit_ids[idx_delete]
    cursor_delete = conn.cursor()
    cursor_delete.execute("DELETE FROM habits WHERE id=?", (habit_id_delete,))
    cursor_delete.execute("DELETE FROM completions WHERE habit_id=?", (habit_id_delete,))
    conn.commit()
    messagebox.showinfo("Success", "Habit deleted successfully.")
    refresh_habits_listbox()


def refresh_habits_listbox():
    habits_listbox.delete(0, tk.END)
    habit_ids.clear()
    cursor_refresh = conn.cursor()
    cursor_refresh.execute(
        "SELECT habits.id, habits.name, habits.goal, habits.frequency, habits.duration, completions.date FROM habits LEFT JOIN completions ON habits.id = completions.habit_id")
    habits = cursor_refresh.fetchall()
    for habit in habits:
        habit_id, habit_name, habit_goal, habit_frequency, habit_duration, completion_date = habit
        habit_ids.append(habit_id)
        display_text = f"{habit_name} - Frequency: {habit_frequency} - Goal: {habit_goal} - Duration: {habit_duration}"
        if completion_date:
            display_text += f" (Completed on {completion_date})"
        habits_listbox.insert(tk.END, display_text)


def analyze_habits():
    global conn  # Add this line to access the global variable conn
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, frequency, COUNT(*) FROM habits LEFT JOIN completions ON habits.id = completions.habit_id GROUP BY name, frequency")
    habits_analysis = cursor.fetchall()

    if not habits_analysis:
        messagebox.showinfo("Info", "No habits tracked yet.")
        return
    else:
        analysis_text = "Habit Analysis:\n"
        daily_habits = []
        weekly_habits = []
        monthly_habits = []
        all_streaks = {}  # Dictionary to store streak for each habit

        for habit in habits_analysis:
            habit_name, frequency, completion_count = habit
            if frequency == "Daily":
                daily_habits.append((habit_name, completion_count))
            elif frequency == "Weekly":
                weekly_habits.append((habit_name, completion_count))
            elif frequency == "Monthly":
                monthly_habits.append((habit_name, completion_count))
            # Calculate and store streak for each habit
            cursor.execute("""SELECT COUNT(*) as streak 
                              FROM completions 
                              JOIN habits ON completions.habit_id = habits.id 
                              WHERE habits.name=? 
                              GROUP BY habit_id""", (habit_name,))
            streak = cursor.fetchone()
            if streak:
                all_streaks[habit_name] = streak[0]

        analysis_text += "\nDaily Habits:\n"
        for habit, count in daily_habits:
            streak_info = f" (Streak: {all_streaks.get(habit, 0)})"  # Get streak info for habit
            analysis_text += f"{habit}: {count} completions{streak_info}\n"

        analysis_text += "\nWeekly Habits:\n"
        for habit, count in weekly_habits:
            streak_info = f" (Streak: {all_streaks.get(habit, 0)})"  # Get streak info for habit
            analysis_text += f"{habit}: {count} completions{streak_info}\n"

        analysis_text += "\nMonthly Habits:\n"
        for habit, count in monthly_habits:
            streak_info = f" (Streak: {all_streaks.get(habit, 0)})"  # Get streak info for habit
            analysis_text += f"{habit}: {count} completions{streak_info}\n"

        # Additional section for longest run streak from all habits
        cursor.execute("""SELECT MAX(streak) FROM (
                            SELECT COUNT(*) as streak 
                            FROM completions 
                            JOIN habits ON completions.habit_id = habits.id 
                            GROUP BY habit_id
                        )""")
        longest_streak_all_habits = cursor.fetchone()[0]
        analysis_text += f"\nLongest Run Streak from All Habits: {longest_streak_all_habits}\n"

        messagebox.showinfo("Habit Analysis", analysis_text)
        # noinspection PyStatementEffect
        n


def get_tracked_habits():
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM habits")
    habits = cursor.fetchall()
    return [habit[0] for habit in habits]


def add_reminder(habit_name, reminder_date, reminder_time):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM habits WHERE name=?", (habit_name,))
    habit_id = cursor.fetchone()
    if habit_id:
        reminder_datetime = f"{reminder_date} {reminder_time}"
        cursor.execute("INSERT INTO reminders (habit_id, reminder_date) VALUES (?, ?)",
                       (habit_id[0], reminder_datetime))
        conn.commit()
        messagebox.showinfo("Success", "Reminder added successfully.")
    else:
        messagebox.showerror("Error", f"No habit found with the name '{habit_name}'.")


# noinspection PyUnboundLocalVariable,PyShadowingNames
def show_reminders():
    reminder_window = tk.Toplevel()
    reminder_window.title("Reminders")
    reminder_window.geometry("400x200")  # Adjusted size

    # noinspection PyShadowingNames
    def delete_reminder(habit_name):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE habit_id=(SELECT id FROM habits WHERE name=?)", (habit_name,))
        conn.commit()
        messagebox.showinfo("Success", "Reminder deleted successfully.")
        reminder_window.destroy()

    cursor = conn.cursor()
    cursor.execute(
        "SELECT habits.name, reminders.reminder_date FROM reminders JOIN habits ON reminders.habit_id = habits.id")
    reminders = cursor.fetchall()

    if reminders:
        for reminder in reminders:
            habit_name, reminder_datetime = reminder
            reminder_date, reminder_time = reminder_datetime.split()
            reminder_text = f"{habit_name}: Date: {reminder_date}, Time: {reminder_time}"
            reminder_label = tk.Label(reminder_window, text=reminder_text)
            reminder_label.pack()

            delete_button = tk.Button(reminder_window, text="Delete Reminder",
                                      command=lambda habit_name=habit_name: delete_reminder(habit_name))
            delete_button.pack()
    else:
        messagebox.showinfo("Reminders", "No reminders set.")


def add_reminder_window():
    reminder_window = tk.Toplevel()
    reminder_window.title("Set Reminder")
    reminder_window.geometry("400x200")  # Adjusted size

    # Display current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tk.Label(reminder_window, text=f"Current Date and Time: {current_datetime}").pack()

    tk.Label(reminder_window, text="Select Habit:").pack()
    habit_names = list(set(get_tracked_habits()))  # Remove duplicates

    # Filter out habits that have reached their goal
    cursor = conn.cursor()
    valid_habit_names = []
    for habit_name in habit_names:
        cursor.execute(
            "SELECT goal, COUNT(completions.id) FROM habits LEFT JOIN completions ON habits.id = completions.habit_id WHERE habits.name=? GROUP BY habits.name",
            (habit_name,))
        goal, count = cursor.fetchone()
        if count < int(goal.split()[0]):  # Assuming goal is in the format "15 of 30 goals"
            valid_habit_names.append(habit_name)

    if not valid_habit_names:
        messagebox.showinfo("Info", "No habits available for setting a reminder.")
        reminder_window.destroy()
        return

    selected_habit = tk.StringVar(reminder_window)
    selected_habit.set(valid_habit_names[0])  # Set default value
    habit_menu = tk.OptionMenu(reminder_window, selected_habit, *valid_habit_names)
    habit_menu.pack()

    tk.Label(reminder_window, text="Reminder Date:").pack()
    reminder_date_entry = DateEntry(reminder_window, date_pattern='yyyy-mm-dd')
    reminder_date_entry.pack()

    tk.Label(reminder_window, text="Reminder Time (HH:MM):").pack()
    reminder_time_entry = tk.Entry(reminder_window)
    reminder_time_entry.pack()

    def set_reminder():
        habit_name = selected_habit.get()
        reminder_date = reminder_date_entry.get()
        reminder_time = reminder_time_entry.get()

        if not habit_name or not reminder_date or not reminder_time:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        add_reminder(habit_name, reminder_date, reminder_time)
        reminder_window.destroy()

    set_reminder_button = tk.Button(reminder_window, text="Set Reminder", command=set_reminder)
    set_reminder_button.pack()


def remind_warning():
    messagebox.showwarning("Warning", "Don't forget to set the reminder time.")

    reminder_window.protocol("WM_DELETE_WINDOW", remind_warning)


def check_reminders():
    cursor = conn.cursor()
    cursor.execute("SELECT habits.name FROM habits JOIN reminders ON habits.id = reminders.habit_id")
    habits_with_reminders = cursor.fetchall()
    today = datetime.today().strftime("%Y-%m-%d")
    for habit in habits_with_reminders:
        habit_name = habit[0]
        cursor.execute(
            "SELECT COUNT(*) FROM completions WHERE habit_id=(SELECT id FROM habits WHERE name=?) AND date=?",
            (habit_name, today))
        if cursor.fetchone()[0] == 0:
            messagebox.showwarning("Erinnerung", f"Du hast vergessen, {habit_name} zu tracken!")


def main():
    create_table()
    root = tk.Tk()
    root.title("Habit Tracker")

    # Adjusting the size of the main window
    root.geometry("750x750")

    # Create Habit Frame
    create_habit_frame = tk.Frame(root)
    create_habit_frame.pack(padx=10, pady=10)

    tk.Label(create_habit_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    global habit_name_entry
    habit_name_entry = tk.Entry(create_habit_frame)
    habit_name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(create_habit_frame, text="Frequency:").grid(row=1, column=0, padx=5, pady=5)
    global habit_frequency_combobox
    frequency_options = ["Daily", "Weekly", "Monthly"]
    habit_frequency_combobox = ttk.Combobox(create_habit_frame, values=frequency_options)
    habit_frequency_combobox.current(0)  # Set default value to Daily
    habit_frequency_combobox.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(create_habit_frame, text="Goal:").grid(row=2, column=0, padx=5, pady=5)
    global habit_goal_entry
    habit_goal_entry = tk.Entry(create_habit_frame)
    habit_goal_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(create_habit_frame, text="Duration (Hours and Minutes):").grid(row=3, column=0, padx=5, pady=5)
    global hours_spinbox, minutes_spinbox
    hours_spinbox = tk.Spinbox(create_habit_frame, from_=0, to=24, width=5)
    hours_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="w")
    minutes_spinbox = tk.Spinbox(create_habit_frame, from_=0, to=59, width=5)
    minutes_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="e")

    create_button = tk.Button(create_habit_frame, text="Create Habit", command=create_habit)
    create_button.grid(row=4, columnspan=2, padx=5, pady=5)

    # Habits List Frame
    habits_list_frame = tk.Frame(root)
    habits_list_frame.pack(padx=10, pady=10)

    tk.Label(habits_list_frame, text="Habits:").pack()
    global habits_listbox
    habits_listbox = tk.Listbox(habits_list_frame, width=100, height=20)  # Increase width and height
    habits_listbox.pack(side=tk.LEFT, padx=5, pady=5)

    scrollbar = tk.Scrollbar(habits_list_frame, orient=tk.VERTICAL)
    scrollbar.config(command=habits_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    habits_listbox.config(yscrollcommand=scrollbar.set)

    # Action Buttons Frame
    action_buttons_frame = tk.Frame(root)
    action_buttons_frame.pack(padx=10, pady=10)

    track_button = tk.Button(action_buttons_frame, text="Track Habit", command=track_habit)
    track_button.grid(row=0, column=0, padx=5, pady=5)

    delete_button = tk.Button(action_buttons_frame, text="Delete Habit", command=delete_habit)
    delete_button.grid(row=0, column=1, padx=5, pady=5)

    analyze_button = tk.Button(action_buttons_frame, text="Analyze Habits", command=analyze_habits)
    analyze_button.grid(row=1, columnspan=2, padx=5, pady=5)

    # Quit Button
    quit_button = tk.Button(action_buttons_frame, text="Quit", command=root.quit)
    quit_button.grid(row=5, columnspan=2, padx=5, pady=5)

    # Reminder Buttons
    add_reminder_button = tk.Button(action_buttons_frame, text="Set Reminder", command=add_reminder_window)
    add_reminder_button.grid(row=2, column=0, padx=5, pady=5)

    show_reminders_button = tk.Button(action_buttons_frame, text="Show Reminders", command=show_reminders)
    show_reminders_button.grid(row=2, column=1, padx=5, pady=5)
    root.after(60000, check_reminders)  # Alle 60 Sekunden die Reminder überprüfen

    refresh_habits_listbox()
    root.mainloop()


if __name__ == "__main__":
    main()

conn.close()

conn.close()
