import pandas as pd
import os

def get_batch_file(batch):
    """Generate the filename for the batch."""
    return f"Students/students_{batch}.csv"

def load_student_data(batch):
    """Load student data for a specific batch."""
    file_path = get_batch_file(batch)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        # Create an empty DataFrame if the file does not exist
        return pd.DataFrame(columns=["Student ID", "Name", "Batch"])

def save_student_data(df, batch):
    """Save student data to a batch-specific file."""
    file_path = get_batch_file(batch)
    df.to_csv(file_path, index=False)

def add_student(student_id, name, batch):
    """Add a student to the batch-specific file."""
    df = load_student_data(batch)
    if student_id in df["Student ID"].values:
        print(f"Student ID {student_id} already exists in batch {batch}.")
    else:
        new_entry = pd.DataFrame({"Student ID": [student_id], "Name": [name], "Batch": [batch]})
        df = pd.concat([df, new_entry], ignore_index=True)
        save_student_data(df, batch)
        print(f"Added student {name} with ID {student_id} to batch {batch}.")

def edit_student(student_id, name=None, batch=None):
    """Edit a student record."""
    # Find the batch for the student_id in all batch files
    batches = [f for f in os.listdir() if f.startswith("students_") and f.endswith(".csv")]
    for batch_file in batches:
        batch_name = batch_file.replace("students_", "").replace(".csv", "")
        df = load_student_data(batch_name)
        if student_id in df["Student ID"].values:
            if name is not None:
                df.loc[df["Student ID"] == student_id, "Name"] = name
            if batch is not None:
                df.loc[df["Student ID"] == student_id, "Batch"] = batch
                # Update batch-specific file
                save_student_data(df, batch)
                print(f"Updated student {student_id} batch to {batch}.")
            else:
                save_student_data(df, batch_name)
                print(f"Updated student {student_id}.")
            return
    print(f"Student ID {student_id} does not exist.")

def delete_student(student_id):
    """Delete a student record from all batch-specific files."""
    batches = [f for f in os.listdir() if f.startswith("students_") and f.endswith(".csv")]
    for batch_file in batches:
        batch_name = batch_file.replace("students_", "").replace(".csv", "")
        df = load_student_data(batch_name)
        if student_id in df["Student ID"].values:
            df = df[df["Student ID"] != student_id]
            save_student_data(df, batch_name)
            print(f"Deleted student {student_id} from batch {batch_name}.")
            return
    print(f"Student ID {student_id} does not exist in any batch.")

def display_students(batch):
    """Display student data from all batch-specific files."""
    df = load_student_data(batch)
    if df.empty:
        print(f"No timetable data available for batch {batch}.")
    else:
        print(df)

def main():
    while True:
        print("\nChoose an action:")
        print("1. Add student")
        print("2. Edit student")
        print("3. Delete student")
        print("4. Display students")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            student_id = input("Enter student ID: ")
            name = input("Enter student name: ")
            batch = input("Enter batch: ")
            add_student(student_id, name, batch)
        elif choice == "2":
            student_id = input("Enter student ID to edit: ")
            name = input("Enter new name (or press Enter to keep current): ")
            batch = input("Enter new batch (or press Enter to keep current): ")
            edit_student(student_id, name or None, batch or None)
        elif choice == "3":
            student_id = input("Enter student ID to delete: ")
            delete_student(student_id)
        elif choice == "4":
            batch = input("Enter class batch: ")
            display_students(batch)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
