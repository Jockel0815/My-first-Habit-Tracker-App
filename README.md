# My-first-Habit-Tracker-App
## Overview

The Habit Tracker is a simple and efficient application designed to help users track their habits and stay motivated to achieve their goals. This application allows users to create habits, track their progress, and analyze their habits to understand their performance better.

## Features

- **Create Habits**: Users can create habits with a specific name, frequency (Daily, Weekly, Monthly), and goal.
- **Track Habits**: Users can track their habits daily, ensuring they are keeping up with their goals.
- **Delete Habits**: Users can delete habits they no longer want to track.
- **Analyze Habits**: Provides an analysis of habits, including the number of completions and the longest run streak for each habit.
- **Add Reminders**: Users can add reminders for their habits to stay on track.
- **View Reminders**: Users can view all reminders set for their habits.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/Jockel0815/My-first-Habit-Tracker-App.git
    cd My-first-Habit-Tracker-App
    ```

2. **Install dependencies**:
    Make sure you have Python installed. You can install the necessary dependencies using pip:
    ```sh
    pip install tk
    ```

3. **Run the application**:
    ```sh
    python habit_tracker.py
    ```

## Usage

### Creating a Habit

1. Enter the name of the habit.
2. Select the frequency (Daily, Weekly, Monthly) from the dropdown menu.
3. Enter the goal for the habit.
4. Click the "Create Habit" button.

### Tracking a Habit

1. Select a habit from the list.
2. Click the "Track Habit" button to mark the habit as completed for today.

### Deleting a Habit

1. Select a habit from the list.
2. Click the "Delete Habit" button to remove the habit from the tracker.

### Analyzing Habits

1. Click the "Analyze Habits" button.
2. A popup will display the analysis of habits, including the number of completions and the longest run streak for each habit.

### Adding a Reminder

1. Click the "Add Reminder" button.
2. Select the habit for which you want to add a reminder.
3. Enter the reminder date and time in the format YYYY-MM-DD HH:MM.
4. Click the "Add Reminder" button to save the reminder.

### Viewing Reminders

1. Click the "Show Reminders" button to view all the reminders set for your habits.

## Database Schema

The Habit Tracker uses an SQLite database with the following schema:

- **habits**: Stores the habits created by the user.
    - `id`: INTEGER PRIMARY KEY
    - `name`: TEXT
    - `frequency`: TEXT
    - `goal`: TEXT

- **completions**: Stores the completion records for the habits.
    - `id`: INTEGER PRIMARY KEY
    - `habit_id`: INTEGER
    - `date`: TEXT
    - UNIQUE(`habit_id`, `date`)
    - FOREIGN KEY (`habit_id`) REFERENCES `habits`(`id`)

- **reminders**: Stores the reminders set for the habits.
    - `id`: INTEGER PRIMARY KEY
    - `habit_id`: INTEGER
    - `reminder_date`: TEXT
    - FOREIGN KEY (`habit_id`) REFERENCES `habits`(`id`)

## Acknowledgments

- **Tkinter**: Used for the GUI components, providing a user-friendly interface for the Habit Tracker application.
- **SQLite**: Employed for the management of the database, facilitating the storage and retrieval of habit-related data in the application.


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
