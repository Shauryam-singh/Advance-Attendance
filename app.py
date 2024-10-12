import os
import pandas as pd
import qrcode
import cv2
import datetime
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from threading import Timer

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Directory paths
STUDENT_DATA_DIR = 'Students'
TIMETABLE_DATA_DIR = 'Timetable'
QR_CODE_DIR = r'static\QR'
ATTENDANCE_DATA_DIR = 'attendance'

# Ensure directories exist
os.makedirs(STUDENT_DATA_DIR, exist_ok=True)
os.makedirs(TIMETABLE_DATA_DIR, exist_ok=True)
os.makedirs(QR_CODE_DIR, exist_ok=True)
os.makedirs(ATTENDANCE_DATA_DIR, exist_ok=True)

# Predefined list of batches
BATCHES = ['CSE_CORE_H', 'ECE_CORE_A', 'MECH_CORE_B', 'EEE_CORE_C']

def get_student_data_file(batch):
    return os.path.join(STUDENT_DATA_DIR, f'students_{batch}.csv')

def get_timetable_file(batch):
    return os.path.join(TIMETABLE_DATA_DIR, f'timetable_{batch}.csv')

def get_attendance_file(batch):
    return os.path.join(ATTENDANCE_DATA_DIR, f'attendance_{batch}.csv')

def generate_qr_code(student_id, name, batch):
    """Generate and save a time-stamped QR code for a student."""
    timestamp = int(time.time()) 
    qr_data = f"{student_id};{name};{batch};{timestamp}"
    qr = qrcode.make(qr_data)
    qr_path = os.path.join(QR_CODE_DIR, f"{name}_QR.png")
    qr.save(qr_path)
    print(f"Time-stamped QR code for {name} generated at {qr_path}.")

def load_students(batch):
    file_path = get_student_data_file(batch)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=['Student ID', 'Name', 'Batch'])

def load_timetable(batch):
    file_path = get_timetable_file(batch)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=['Subject Name', 'Start Time', 'End Time'])

@app.route('/')
def index():
    return render_template('index.html', batches=BATCHES)

@app.route('/generate_qr_codes', methods=['GET'])
def generate_qr_codes():
    batch = request.args.get('batch')
    if not batch:
        flash('No batch selected for QR code generation.')
        return redirect(url_for('index'))

    students_df = load_students(batch)
    if students_df.empty:
        flash(f"No students found for batch {batch}.")
    else:
        for _, student in students_df.iterrows():
            generate_qr_code(student['Student ID'], student['Name'], student['Batch'])
        flash(f"QR codes generated for batch {batch}.")

    return redirect(url_for('index'))

@app.route('/mark_attendance', methods=['GET'])
def mark_attendance():
    batch = request.args.get('batch')
    if not batch:
        flash('No batch selected for marking attendance.')
        return redirect(url_for('index'))

    timetable_df = load_timetable(batch)
    if timetable_df.empty:
        flash(f"No timetable found for batch {batch}.")
        return redirect(url_for('index'))

    students_df = load_students(batch)
    if students_df.empty:
        flash(f"No students found for batch {batch}.")
        return redirect(url_for('index'))

    valid_ids = set(students_df['Student ID'].values)

    attendance_df = pd.DataFrame(columns=["Student ID", "Name", "Timestamp", "Subject", "Batch"])
    attendance_df = read_qr_code(attendance_df, timetable_df, valid_ids, batch)

    # Save the attendance to a file
    attendance_file = get_attendance_file(batch)
    if not attendance_df.empty:
        attendance_df.to_csv(attendance_file, index=False)
        flash(f"Attendance data saved to {attendance_file}.")
    else:
        flash("No attendance data was recorded.")

    return redirect(url_for('index'))

@app.route('/show_qr_codes', methods=['GET'])
def show_qr_codes():
    # Use the full path to the QR code directory under 'static/QR/'
    qr_code_dir = os.path.join(os.getcwd(), 'static', 'QR')  # Ensure using full path

    # Debugging print statement
    print(f"Looking in {qr_code_dir} for QR code files.")
    
    # List all QR codes in the directory
    qr_files = [f for f in os.listdir(qr_code_dir) if f.endswith('.png')]

    # Debugging print statement to check QR files found
    print(f"Found QR files: {qr_files}")

    if not qr_files:
        flash('No QR codes found.')
        return redirect(url_for('index'))

    return render_template('show_qr_codes.html', qr_files=qr_files)

def read_qr_code(attendance, timetable, valid_ids, batch):
    """Read QR codes from the webcam and mark attendance."""
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    TIME_WINDOW = 300
    while True:
        _, frame = cap.read()
        if frame is None:
            print("Failed to capture image from webcam.")
            break

        data, _, _ = detector.detectAndDecode(frame)
        if data:
            try:
                student_id, name, qr_batch, qr_timestamp = data.split(';')
                qr_timestamp = int(qr_timestamp)
                current_timestamp = int(time.time())
                
                # Check if the QR code is within the valid time window
                if current_timestamp - qr_timestamp <= TIME_WINDOW:
                    print(f"QR Code Data: Student ID={student_id}, Name={name}, Batch={qr_batch}")
                    if student_id in valid_ids and qr_batch == batch:
                        now = datetime.datetime.now()
                        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                        subject, start_time, end_time = get_current_subject(now, timetable)
                        if subject:
                            new_entry = pd.DataFrame({
                                "Student ID": [student_id],
                                "Name": [name],
                                "Timestamp": [timestamp],
                                "Subject": [subject],
                                "Batch": [batch]
                            })
                            attendance = pd.concat([attendance, new_entry], ignore_index=True)
                            print(f"Marked attendance for {name} in {subject} at {timestamp}")
                            cv2.waitKey(1000)
                        else:
                            print(f"No lecture currently. Unable to mark attendance for {name} at {timestamp}")
                    else:
                        print("Invalid batch or student ID.")
                else:
                    print("QR code is expired.")
            except ValueError:
                print("Invalid QR code data format.")

        cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return attendance

def get_current_subject(now, timetable):
    """Get the current subject based on the timetable."""
    for _, row in timetable.iterrows():
        start_time = datetime.datetime.strptime(row["Start Time"], "%I:%M %p").time()
        end_time = datetime.datetime.strptime(row["End Time"], "%I:%M %p").time()
        if start_time <= now.time() <= end_time:
            return row["Subject Name"], start_time, end_time
    return None, None, None

@app.route('/manage_students', methods=['GET', 'POST'])
def manage_students():
    if request.method == 'POST':
        batch = request.form['batch']
        student_id = request.form['student_id']
        student_name = request.form['student_name']

        students_df = load_students(batch)

        if student_id in students_df['Student ID'].values:
            flash("Student ID already exists.")
        else:
            new_student = pd.DataFrame({'Student ID': [student_id], 'Name': [student_name], 'Batch': [batch]})
            students_df = pd.concat([students_df, new_student], ignore_index=True)
            students_df.to_csv(get_student_data_file(batch), index=False)
            flash(f"Student {student_name} added to batch {batch}.")

        return redirect(url_for('manage_students'))

    return render_template('manage_students.html', batches=BATCHES)

@app.route('/manage_timetable', methods=['GET', 'POST'])
def manage_timetable():
    if request.method == 'POST':
        batch = request.form['batch']
        subject_name = request.form['subject_name']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        timetable_df = load_timetable(batch)

        new_entry = pd.DataFrame({'Subject Name': [subject_name], 'Start Time': [start_time], 'End Time': [end_time]})
        timetable_df = pd.concat([timetable_df, new_entry], ignore_index=True)

        timetable_df.to_csv(get_timetable_file(batch), index=False)
        flash(f"Timetable updated for batch {batch}.")
        return redirect(url_for('manage_timetable'))

    return render_template('manage_timetable.html', batches=BATCHES)

def periodically_generate_qr_codes(batch):
    students_df = load_students(batch)
    for _, student in students_df.iterrows():
        generate_qr_code(student['Student ID'], student['Name'], student['Batch'])
    print(f"Periodically generated QR codes for batch {batch}.")
    
    # Schedule the next generation in the future
    Timer(60 * 5, periodically_generate_qr_codes, [batch]).start()
# Call this function to start periodic QR code generation for each batch
for batch in BATCHES:
    periodically_generate_qr_codes(batch)
if __name__ == '__main__':
    app.run(debug=True)