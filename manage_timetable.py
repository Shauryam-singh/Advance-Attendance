import pandas as pd
import os
from datetime import datetime, timedelta

# Function to get the file name for a specific batch
def get_timetable_file(batch):
    return f"Timetable/timetable_{batch}.csv"

# Ensure the timetable file for a batch exists
def ensure_timetable_file_exists(batch):
    timetable_file = get_timetable_file(batch)
    if not os.path.exists(timetable_file):
        initial_df = pd.DataFrame(columns=["Day", "Subject Code", "Subject Name", "Start Time", "End Time"])
        initial_df.to_csv(timetable_file, index=False)

def load_timetable_data(batch):
    timetable_file = get_timetable_file(batch)
    return pd.read_csv(timetable_file)

def save_timetable_data(df, batch):
    timetable_file = get_timetable_file(batch)
    df.to_csv(timetable_file, index=False)

def add_subject(day, batch, subject_code, subject_name, start_time):
    ensure_timetable_file_exists(batch)
    df = load_timetable_data(batch)

    # Check for duplicate subject code on the same day for the batch
    if ((df["Subject Code"] == subject_code) & (df["Day"] == day)).any():
        print(f"Subject code {subject_code} already exists for {day} in batch {batch}.")
    else:
        # Calculate end time 50 minutes after the start time
        start_time_obj = datetime.strptime(start_time, "%I:%M %p")
        end_time_obj = start_time_obj + timedelta(minutes=50)
        end_time = end_time_obj.strftime("%I:%M %p")

        new_entry = pd.DataFrame({
            "Day": [day],
            "Subject Code": [subject_code],
            "Subject Name": [subject_name],
            "Start Time": [start_time],
            "End Time": [end_time]
        })
        df = pd.concat([df, new_entry], ignore_index=True)
        save_timetable_data(df, batch)
        print(f"Added subject {subject_name} with code {subject_code} on {day} in batch {batch}.")

def edit_subject(batch, subject_code, day, subject_name=None, start_time=None):
    df = load_timetable_data(batch)
    if not ((df["Subject Code"] == subject_code) & (df["Day"] == day)).any():
        print(f"Subject code {subject_code} does not exist on {day} in batch {batch}.")
    else:
        if subject_name is not None:
            df.loc[(df["Subject Code"] == subject_code) & (df["Day"] == day), "Subject Name"] = subject_name
        if start_time is not None:
            # Calculate new end time 50 minutes after the start time
            start_time_obj = datetime.strptime(start_time, "%I:%M %p")
            end_time_obj = start_time_obj + timedelta(minutes=50)
            end_time = end_time_obj.strftime("%I:%M %p")
            df.loc[(df["Subject Code"] == subject_code) & (df["Day"] == day), "Start Time"] = start_time
            df.loc[(df["Subject Code"] == subject_code) & (df["Day"] == day), "End Time"] = end_time
        save_timetable_data(df, batch)
        print(f"Updated subject {subject_code} on {day} in batch {batch}.")

def delete_subject(batch, subject_code, day):
    df = load_timetable_data(batch)
    if not ((df["Subject Code"] == subject_code) & (df["Day"] == day)).any():
        print(f"Subject code {subject_code} does not exist on {day} in batch {batch}.")
    else:
        df = df[~((df["Subject Code"] == subject_code) & (df["Day"] == day))]
        save_timetable_data(df, batch)
        print(f"Deleted subject {subject_code} on {day} in batch {batch}.")

def display_timetable(batch):
    df = load_timetable_data(batch)
    if df.empty:
        print(f"No timetable data available for batch {batch}.")
    else:
        print(df)

def main():
    while True:
        print("\nChoose an action:")
        print("1. Add subject")
        print("2. Edit subject")
        print("3. Delete subject")
        print("4. Display timetable")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            day = input("Enter day (e.g., Monday): ")
            batch = input("Enter class batch: ")
            subject_code = input("Enter subject code: ")
            subject_name = input("Enter subject name: ")
            start_time = input("Enter start time (e.g., 09:00 AM): ")
            add_subject(day, batch, subject_code, subject_name, start_time)
        elif choice == "2":
            day = input("Enter day (e.g., Monday): ")
            batch = input("Enter class batch: ")
            subject_code = input("Enter subject code to edit: ")
            subject_name = input("Enter new subject name (or press Enter to keep current): ")
            start_time = input("Enter new start time (or press Enter to keep current): ")
            edit_subject(batch, subject_code, day, subject_name or None, start_time or None)
        elif choice == "3":
            day = input("Enter day (e.g., Monday): ")
            batch = input("Enter class batch: ")
            subject_code = input("Enter subject code to delete: ")
            delete_subject(batch, subject_code, day)
        elif choice == "4":
            batch = input("Enter class batch: ")
            display_timetable(batch)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
