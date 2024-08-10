import qrcode
import cv2
import pandas as pd
import datetime
import os

# Create directory for QR codes if it doesn't exist
if not os.path.exists("QR"):
    os.makedirs("QR")

def generate_qr_code(student_id, name, batch):
    """Generate and save a QR code for a student."""
    qr_data = f"{student_id};{name};{batch}"
    qr = qrcode.make(qr_data)
    qr.save(f"QR/{name}_QR.png")
    print(f"QR code for {name} generated.")

def load_students(file_path):
    """Load student data from a CSV file."""
    df = pd.read_csv(file_path)
    print(f"Loaded students data:\n{df}")  # Debug print
    return df

def load_timetable(file_path):
    """Load timetable data from a CSV file."""
    return pd.read_csv(file_path)

def get_current_subject(now, timetable):
    """Get the current subject based on the timetable."""
    for _, row in timetable.iterrows():
        start_time = datetime.datetime.strptime(row["Start Time"], "%I:%M %p").time()
        end_time = datetime.datetime.strptime(row["End Time"], "%I:%M %p").time()
        if start_time <= now.time() <= end_time:
            return row["Subject Name"], start_time, end_time
    return None, None, None

def has_attendance_been_marked(attendance, student_id, subject, start_time, end_time):
    """Check if attendance has already been marked for the student for the given subject within the time window."""
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # Convert current time to a comparable format
    current_time = now.time()

    # Filter attendance records for the same subject and student
    time_window_attendance = attendance[
        (attendance["Student ID"] == student_id) &
        (attendance["Subject"] == subject)
    ]

    # Check if any record falls within the current time window
    for _, row in time_window_attendance.iterrows():
        record_time = datetime.datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S").time()
        if start_time <= record_time <= end_time:
            return True
    return False

def mark_attendance(student_id, name, attendance, timetable, batch):
    """Mark attendance for a student."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject, start_time, end_time = get_current_subject(datetime.datetime.now(), timetable)
    if subject is not None:
        if not has_attendance_been_marked(attendance, student_id, subject, start_time, end_time):
            new_entry = pd.DataFrame({"Student ID": [student_id], "Name": [name], "Timestamp": [timestamp], "Subject": [subject], "Batch": [batch]})
            attendance = pd.concat([attendance, new_entry], ignore_index=True)
            print(f"Marked attendance for {name} in {subject} at {timestamp}")
        else:
            print(f"Attendance already marked for {name} in {subject} during this lecture.")
    else:
        print(f"No lecture currently. Unable to mark attendance for {name} at {timestamp}")
    return attendance

def read_qr_code(attendance, timetable, valid_ids, batch):
    """Read QR codes from the webcam and mark attendance."""
    # Open the webcam
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        _, frame = cap.read()
        if frame is None:
            print("Failed to capture image from webcam.")
            break

        data, _, _ = detector.detectAndDecode(frame)
        if data:
            # Split data into student ID, name, and batch
            try:
                student_id, name, qr_batch = data.split(';')
                print(f"QR Code Data: Student ID={student_id}, Name={name}, Batch={qr_batch}")  # Debug print
                if student_id in valid_ids and qr_batch == batch:
                    attendance = mark_attendance(student_id, name, attendance, timetable, batch)
                    cv2.waitKey(1000)  # Wait for 1 second
                else:
                    print(f"Student ID {student_id} not found, batch mismatch, or incorrect branch.")
            except ValueError:
                print("Invalid QR code data format.")

        cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return attendance

# Get user input for batch name
batch = input("Enter the batch name (e.g., CSE_CORE_H): ").strip()
students_file = f"Students/students_{batch}.csv"
timetable_file = f"Timetable/timetable_{batch}.csv"
attendance_file = f"attendance_{batch}.csv"

# Load students data and verify the batch information
students_df = load_students(students_file)
timetable_df = load_timetable(timetable_file)

# Filter students for the current batch
batch_students_df = students_df[students_df['Batch'] == batch]
if batch_students_df.empty:
    print(f"No students found for batch {batch}. Exiting.")
    exit()

# Generate QR codes for each student in the batch
for _, student in batch_students_df.iterrows():
    generate_qr_code(student['Student ID'], student['Name'], student['Batch'])

# Initialize attendance DataFrame
attendance = pd.DataFrame(columns=["Student ID", "Name", "Timestamp", "Subject", "Batch"])

# Create a set of valid student IDs for the current batch
valid_ids = set(batch_students_df['Student ID'].values)

# Print valid student IDs and their batches
print(f"Valid student IDs for batch {batch}: {valid_ids}")
print(f"Students Data:\n{batch_students_df}")

# Run the QR code reader
attendance = read_qr_code(attendance, timetable_df, valid_ids, batch)

# Check if DataFrame is not empty before saving
if not attendance.empty:
    try:
        print("Saving attendance data...")
        attendance.to_csv(attendance_file, index=False)
        print(f"Attendance data saved to {attendance_file}")
    except Exception as e:
        print(f"Error saving attendance data: {e}")
else:
    print("Attendance DataFrame is empty. No data was saved.")
