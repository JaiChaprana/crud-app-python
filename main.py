import tkinter as tk
from tkinter import messagebox

# Import the architectural boundaries
from auth import LoginWindow
from database import Database
from processor import DataProcessor

# Import the isolated UI Dashboards
from admin_portal import AdminApp
from professor_dashboard import ProfessorApp
from student_dashboard import StudentDashboard

if __name__ == "__main__":
    root = tk.Tk()

    # ANCHOR INITIALIZE THE ENGINES EXACTLY ONCE
    db = Database()
    engine = DataProcessor(db.conn)


    def on_login_success(username, role, linked_id):
        # ANCHOR CLOSE THE LOGIN SCREEN
        for widget in root.winfo_children():
            widget.destroy()

        # ANCHOR ROLE BASED ACCESS SYSTEM
        if role == "admin":
            AdminApp(root, username, db, engine)
        elif role == "professor":
            ProfessorApp(root, username, linked_id, db, engine)
        elif role == "student":
            StudentDashboard(root, username, linked_id, db, engine)
        else:
            messagebox.showerror("Routing Error", "Unknown role assigned to user.")
            root.quit()

    # ANCHOR START OUR APP ALWAYS WITH THE LOGIN WINDOW
    LoginWindow(root, on_login_success)
    root.mainloop()
