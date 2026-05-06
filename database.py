import sqlite3
from datetime import datetime
import hashlib


class Database:
    def __init__(self, db_name="student_system.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        self.valid_columns = {
            "sap",
            "name",
            "course",
            "program",
            "batch",
            "age",
            "semester",
            "email",
        }

        self.programs = [
            "B.Tech",
            "B.Sc",
            "B.Des",
            "BBA",
            "BA",
            "B.Com",
            "B.Pharm",
            "LLB",
            "MBA",
            "M.Tech",
            "M.Sc",
            "M.Des",
            "MA",
            "LLM",
            "Ph.D",
        ]

        self.courses_map = {
            "B.Tech": [
                "Computer Science",
                "Mechanical",
                "Civil",
                "Electrical",
                "Aerospace",
            ],
            "B.Sc": [
                "Physics",
                "Mathematics",
                "Chemistry",
                "Computer Science",
            ],
            "B.Des": [
                "Product Design",
                "Transportation Design",
                "Interaction Design",
            ],
            "BBA": ["General", "Finance", "Marketing", "Human Resources"],
            "BA": ["English", "History", "Political Science", "Economics"],
            "B.Com": ["General", "Taxation", "Accounting"],
            "B.Pharm": ["Pharmacy"],
            "LLB": ["Law"],
            "MBA": ["Finance", "Marketing", "Operations", "Human Resources"],
            "M.Tech": [
                "Computer Science",
                "Structural Engineering",
                "Thermal Engineering",
            ],
            "M.Sc": ["Physics", "Mathematics", "Chemistry", "Data Science"],
            "M.Des": ["Industrial Design", "Visual Communication"],
            "MA": ["English", "Economics", "Sociology"],
            "LLM": ["Corporate Law", "Criminal Law"],
            "Ph.D": ["Research"],
        }

        # NOTE If the TABLES Do not ACCESS
        self.init_tables()
        # NOTE For Fallback ACCESS
        self.ensure_admin_exists()

    def init_tables(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT, role TEXT, linked_id TEXT)"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS students (sap TEXT PRIMARY KEY, name TEXT, course TEXT, program TEXT, batch TEXT, age INTEGER, semester INTEGER, email TEXT)"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, professor_username TEXT, program TEXT, course TEXT, semester INTEGER, batch TEXT, subject TEXT, FOREIGN KEY(professor_username) REFERENCES users(username))"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS grades_detailed (sap TEXT, semester INTEGER, subject TEXT, mid_sem REAL DEFAULT 0.0, end_sem REAL DEFAULT 0.0, ct_1 REAL DEFAULT 0.0, ct_2 REAL DEFAULT 0.0, quiz_1 REAL DEFAULT 0.0, quiz_2 REAL DEFAULT 0.0, is_locked INTEGER DEFAULT 0, PRIMARY KEY (sap, semester, subject))"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS curriculum (id INTEGER PRIMARY KEY AUTOINCREMENT, program TEXT, course TEXT, semester INTEGER, subject TEXT, credits INTEGER)"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS logs (action TEXT, details TEXT, timestamp TEXT, username TEXT)"""
        )
        self.conn.commit()

    # ANCHOR --- AUTHENTICATION & ROLES ---
    # NOTE Encryption of PASSWORDS
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, role, linked_id=""):
        hashed = self.hash_password(password)
        try:
            # NOTE Enforce case-insensitive usernames
            self.cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?)",
                (username.lower(), hashed, role, linked_id),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username, password):
        hashed = self.hash_password(password)
        self.cursor.execute(
            "SELECT role, linked_id FROM users WHERE username=? AND password_hash=?",
            (username.lower(), hashed),
        )
        return self.cursor.fetchone()

    def ensure_admin_exists(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            self.register_user("admin", "12345", "admin", "SUPERUSER")

    def delete_user(self, username):
        self.cursor.execute(
            "DELETE FROM assignments WHERE professor_username=?", (username,)
        )
        self.cursor.execute("DELETE FROM users WHERE username=?", (username,))
        self.conn.commit()

    # ANCHOR --- PROFESSOR ASSIGNMENTS ---
    def assign_professor(self, prof_user, program, course, semester, batch, subject):
        self.cursor.execute(
            "SELECT COUNT(*) FROM assignments WHERE professor_username=?",
            (prof_user,),
        )
        if self.cursor.fetchone()[0] >= 3:
            return False, "Professor already assigned to maximum of 3 batches."
        self.cursor.execute(
            "INSERT INTO assignments (professor_username, program, course, semester, batch, subject) VALUES (?, ?, ?, ?, ?, ?)",
            (prof_user, program, course, semester, batch, subject),
        )
        self.conn.commit()
        return True, "Assigned successfully."

    def get_professor_batches(self, prof_user):
        self.cursor.execute(
            "SELECT program, course, semester, batch, subject FROM assignments WHERE professor_username=?",
            (prof_user,),
        )
        return self.cursor.fetchall()

    # ANCHOR --- DETAILED GRADES ---
    def update_detailed_grade(self, sap, semester, subject, component, marks):
        self.cursor.execute(
            "INSERT OR IGNORE INTO grades_detailed (sap, semester, subject) VALUES (?, ?, ?)",
            (sap, semester, subject),
        )
        valid_components = [
            "mid_sem",
            "end_sem",
            "ct_1",
            "ct_2",
            "quiz_1",
            "quiz_2",
        ]
        if component in valid_components:
            sql = f"UPDATE grades_detailed SET {component} = ? WHERE sap = ? AND semester = ? AND subject = ?"
            self.cursor.execute(sql, (marks, sap, semester, subject))
            self.conn.commit()

    def get_detailed_grades(self, sap):
        self.cursor.execute(
            "SELECT * FROM grades_detailed WHERE sap=?", (sap,)
        )
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_all_detailed_grades(self):
        """Fetches all grades across the system for Z-Score and Bottleneck analysis."""
        self.cursor.execute("SELECT * FROM grades_detailed")
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    # ANCHOR --- DATA UTILITIES ---
    def sanitize_data(self, data_dict):
        clean_data = {}
        for k, v in data_dict.items():
            if isinstance(v, str):
                cleaned_str = " ".join(v.split())
                if k == "email":
                    clean_data[k] = cleaned_str.lower()
                elif k == "sap":
                    clean_data[k] = cleaned_str.upper()
                elif k in ["program", "batch"]:
                    clean_data[k] = cleaned_str
                else:
                    clean_data[k] = cleaned_str.title()
            else:
                clean_data[k] = v
        return clean_data

    # ANCHOR -- STUDENT CRUD & FILTERS ---
    def add_student(self, data_dict):
        safe_data = {
            k: v for k, v in data_dict.items() if k in self.valid_columns
        }
        clean_data = self.sanitize_data(safe_data)
        columns = ", ".join(clean_data.keys())
        placeholders = ", ".join(["?"] * len(clean_data))
        sql = f"INSERT INTO students ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(clean_data.values()))
        self.conn.commit()

    def update_student(self, sap, gui_data):
        # NOTE Merge-on-Update Logic: Only update fields that are not empty strings
        updates = {
            k: v
            for k, v in gui_data.items()
            if k in self.valid_columns and v != "" and k != "sap"
        }
        clean_updates = self.sanitize_data(updates)
        if not clean_updates:
            return False
        set_clause = ", ".join(
            [f"{column} = ?" for column in clean_updates.keys()]
        )
        values = list(clean_updates.values())
        values.append(sap)
        sql = f"UPDATE students SET {set_clause} WHERE sap = ?"
        self.cursor.execute(sql, tuple(values))
        self.conn.commit()
        return True

    def get_student(self, sap):
        self.cursor.execute("SELECT * FROM students WHERE sap=?", (sap,))
        return self.cursor.fetchone()

    def get_all_students(self):
        self.cursor.execute(
            "SELECT sap, name, course, program, batch, age, semester, email FROM students"
        )
        return self.cursor.fetchall()

    def get_cohort_data(self, program, semester):
        """Fetches subset of students for Heuristic Auto-Fill (Smart Defaults)."""
        self.cursor.execute(
            "SELECT age, batch FROM students WHERE program=? AND semester=?",
            (program, semester),
        )
        return self.cursor.fetchall()

    def filter_students(
        self, query_text=None, program=None, semester=None, batch=None
    ):
        sql = "SELECT * FROM students WHERE 1=1"
        params = []
        if query_text:
            sql += " AND (name LIKE ? OR sap LIKE ?)"
            params.extend([f"%{query_text}%", f"%{query_text}%"])
        if program and program != "All Programs":
            sql += " AND program = ?"
            params.append(program)
        if semester and semester != "All Semesters":
            sql += " AND semester = ?"
            params.append(int(semester))
        if batch and batch != "All Batches":
            sql += " AND batch = ?"
            params.append(batch)
        self.cursor.execute(sql, tuple(params))
        return self.cursor.fetchall()

    def delete_student(self, sap):
        self.cursor.execute("DELETE FROM grades_detailed WHERE sap=?", (sap,))
        self.cursor.execute("DELETE FROM students WHERE sap=?", (sap,))
        self.conn.commit()

    # ANCHOR --- LOGGING & SECURITY ---
    def log_action(self, user, action, details):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO logs VALUES (?, ?, ?, ?)",
            (action, details, timestamp, user),
        )
        self.conn.commit()

    def get_recent_logs(self, user, seconds_window):
        """Fetches logs for a specific user within a given timeframe to calculate Action Velocity."""
        time_threshold = (
            datetime.now() - timedelta(seconds=seconds_window)
        ).strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "SELECT action FROM logs WHERE username=? AND timestamp >= ?",
            (user, time_threshold),
        )
        return self.cursor.fetchall()

    # ANCHOR --- CURRICULUM ENGINE ---
    def add_curriculum_subject(
        self, program, course, semester, subject, credits
    ):
        clean_program = " ".join(program.split())
        clean_course = " ".join(course.split())
        clean_subject = " ".join(subject.split()).title()

        self.cursor.execute(
            "SELECT * FROM curriculum WHERE program COLLATE NOCASE = ? AND course COLLATE NOCASE = ? AND semester=? AND subject COLLATE NOCASE = ?",
            (clean_program, clean_course, semester, clean_subject),
        )
        if self.cursor.fetchone():
            return False

        self.cursor.execute(
            "INSERT INTO curriculum (program, course, semester, subject, credits) VALUES (?, ?, ?, ?, ?)",
            (clean_program, clean_course, semester, clean_subject, credits),
        )
        self.conn.commit()
        return True

    def get_curriculum(self, program, course, semester):
        self.cursor.execute(
            "SELECT subject FROM curriculum WHERE program COLLATE NOCASE = ? AND course COLLATE NOCASE = ? AND semester=?",
            (program, course, semester),
        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_subject_credits(self, program, course, semester, subject):
        self.cursor.execute(
            "SELECT credits FROM curriculum WHERE program COLLATE NOCASE = ? AND course COLLATE NOCASE = ? AND semester=? AND subject COLLATE NOCASE = ?",
            (program, course, semester, subject),
        )
        res = self.cursor.fetchone()
        return res[0] if res else None

    def get_all_curriculum(self):
        self.cursor.execute(
            "SELECT program, course, semester, subject, credits FROM curriculum ORDER BY program, course, semester"
        )
        return self.cursor.fetchall()

    def delete_curriculum_subject(self, program, course, semester, subject):
        self.cursor.execute(
            "DELETE FROM curriculum WHERE program=? AND course=? AND semester=? AND subject=?",
            (program, course, semester, subject),
        )
        self.conn.commit()

    # ANCHOR --- GRADING ENGINE (CGPA / SGPA) ---
    def calculate_gpa(self, sap):
        grades = self.get_detailed_grades(sap)
        student_info = self.get_student(sap)
        if not student_info:
            return {}, 0.0, []

        program, course = student_info[3], student_info[2]

        def get_grade_point(total_marks):
            if total_marks >= 90:
                return 10, "O"
            elif total_marks >= 80:
                return 9, "A+"
            elif total_marks >= 70:
                return 8, "A"
            elif total_marks >= 60:
                return 7, "B+"
            elif total_marks >= 50:
                return 6, "B"
            elif total_marks >= 40:
                return 5, "C"
            else:
                return 0, "F"

        semester_data = {}
        grade_records = [] #

        for g in grades:
            # FIXME  Cast string semester to int to prevent UI crashes
            sem = int(g["semester"])
            subj = g["subject"]

            total_marks = (
                g["mid_sem"]
                + g["end_sem"]
                + g["ct_1"]
                + g["ct_2"]
                + g["quiz_1"]
                + g["quiz_2"]
            )
            grade_point, letter_grade = get_grade_point(total_marks)
            credits = self.get_subject_credits(program, course, sem, subj)
            if credits is None:
                credits = 3

            credit_points = grade_point * credits

            if sem not in semester_data:
                semester_data[sem] = {
                    "total_credit_points": 0,
                    "total_credits": 0,
                }

            semester_data[sem]["total_credit_points"] += credit_points
            semester_data[sem]["total_credits"] += credits

            grade_records.append(
                {
                    "semester": sem,
                    "subject": subj,
                    "total_marks": total_marks,
                    "credits": credits,
                    "grade_point": grade_point,
                    "letter_grade": letter_grade,
                }
            )

        sgpa_dict = {}
        total_cumulative_points = total_cumulative_credits = 0

        for sem, data in semester_data.items():
            if data["total_credits"] > 0:
                sgpa = data["total_credit_points"] / data["total_credits"]
                sgpa_dict[sem] = round(sgpa, 2)
                total_cumulative_points += data["total_credit_points"]
                total_cumulative_credits += data["total_credits"]
            else:
                sgpa_dict[sem] = 0.0

        cgpa = (
            round(total_cumulative_points / total_cumulative_credits, 2)
            if total_cumulative_credits > 0
            else 0.0
        )
        return sgpa_dict, cgpa, grade_records
