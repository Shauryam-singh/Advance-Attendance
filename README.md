# QR Code Attendance System

This project is a Flask-based web application that automates attendance management using QR codes. The system generates time-stamped QR codes for students, which are then scanned to mark attendance within a specific time window. The application includes functionalities for managing student data, timetables, and attendance records.

## Features

- **Time-Stamped QR Codes:** Each QR code contains a time-stamp to ensure the validity within a specified time window (e.g., 5 minutes).
- **Automated Attendance:** Attendance is marked by scanning QR codes, which are validated based on the time-stamp and batch.
- **Periodic QR Code Generation:** QR codes are automatically regenerated every 5 minutes, ensuring they remain valid.
- **Batch Management:** Supports multiple batches, with separate data files for students, timetables, and attendance.
- **User-Friendly Interface:** A web interface allows easy management of students and timetables, as well as generating and scanning QR codes.

## Directory Structure

```
QR-Code-Attendance-System/
│
├── Students/
│   └── students_<batch_name>.csv      # CSV files containing student data for each batch
│
├── Timetable/
│   └── timetable_<batch_name>.csv     # CSV files containing timetable data for each batch
│
├── QR/
│   └── *.png                          # Generated QR codes for each student
│
├── attendance/
│   └── attendance_<batch_name>.csv    # CSV files where attendance records are stored
│
├── templates/
│   ├── index.html                     # Homepage template
│   ├── manage_students.html           # Manage students template
│   └── manage_timetable.html          # Manage timetable template
│
├── app.py                             # Main Flask application file
├── README.md                          # Project README file
└── requirements.txt                   # Python dependencies
```

## Prerequisites

- Flask
- Pandas
- OpenCV
- qrcode

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/QR-Code-Attendance-System.git
   cd QR-Code-Attendance-System
   ```

2. **Install Dependencies:**

   Use `pip` to install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Directories:**

   Ensure that the following directories exist:

   - `Students`
   - `Timetable`
   - `QR`
   - `attendance`

   These directories will be automatically created if they do not exist.

4. **Prepare Student and Timetable Data:**

   - Place student data in CSV files inside the `Students` directory (e.g., `students_CSE_CORE_H.csv`).
   - Place timetable data in CSV files inside the `Timetable` directory (e.g., `timetable_CSE_CORE_H.csv`).

   Each student file should have the following columns: `Student ID`, `Name`, `Batch`.

   Each timetable file should have the following columns: `Subject Name`, `Start Time`, `End Time`.

5. **Run the Application:**

   Start the Flask application by running:

   ```bash
   python app.py
   ```

6. **Access the Web Interface:**

   Open your browser and go to `http://127.0.0.1:5000/`.

## Usage

### Home Page

The home page allows you to select a batch and perform various actions:

- **Generate QR Codes:** Generate time-stamped QR codes for all students in the selected batch.
- **Mark Attendance:** Start the QR code scanner to mark attendance for the selected batch.
- **Manage Students:** Add or remove students from the selected batch.
- **Manage Timetable:** Add or update subjects and their corresponding times for the selected batch.

### Managing Students

- Navigate to the "Manage Students" page.
- Select a batch and enter the student details (ID and Name).
- Submit to add the student to the batch.

### Managing Timetable

- Navigate to the "Manage Timetable" page.
- Select a batch and enter the subject details (Name, Start Time, End Time).
- Submit to add the subject to the timetable for the batch.

### Generating and Scanning QR Codes

- QR codes are generated for students in the selected batch and stored in the `QR` directory.
- The scanner captures and decodes the QR code, marks attendance if the code is valid (within the time window).

### Attendance Records

- Attendance records are stored in CSV files within the `attendance` directory.
- The file format is `attendance_<batch_name>.csv`.

## Future Enhancements

- Add a feature to send attendance reports via email.
- Implement a feature to automatically archive old attendance records.
- Integrate face recognition to enhance security during QR code scanning.
- Allow administrators to configure time windows and other parameters through the web interface.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For any inquiries, please contact `shauryamsingh9@gmail.com`.

---