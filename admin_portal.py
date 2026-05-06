import tkinter as tk
from tkinter import ttk
from admin_tab_students import StudentTab
from admin_tab_staff import StaffTab

class AdminApp:
    def __init__(self, root, user, db, engine):
        self.root = root
        self.user = user
        self.db = db
        self.engine = engine

        self.root.title(f"University ERP | Admin Portal | User: {self.user}")
        self.root.geometry("1350x800")
        self.root.configure(bg="#ecf0f1")

        self.setup_styles()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.frame_students = tk.Frame(self.notebook, bg="#ffffff")
        self.frame_staff = tk.Frame(self.notebook, bg="#ffffff")

        self.notebook.add(self.frame_students, text=" Student Management ")
        self.notebook.add(self.frame_staff, text=" Staff & User Management ")

        # Dependency Injection: Pass db and engine down to the tabs
        self.staff_tab = StaffTab(self.frame_staff, self.db, self.user, self.root, self.engine)
        self.student_tab = StudentTab(self.frame_students, self.db, self.engine, self.user, self.root, self.staff_tab.refresh_users_table)

        self.setup_sync_button()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        # Enforcing your design constraints: #2c3e50 headers, rowheight=30
        style.configure("Treeview.Heading", background="#2c3e50", foreground="white", font=("Arial", 10, "bold"), padding=5)
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.map("Treeview", background=[('selected', '#3498db')])
        self.root.tree_style = style

    def setup_sync_button(self):
        sync_btn = ttk.Button(self.root, text="Global Sync / Refresh", command=self.sync_all)
        sync_btn.pack(side="bottom", anchor="e", padx=20, pady=10)

    def sync_all(self):
        self.student_tab.refresh_table()
        self.student_tab.clear_form()
        self.staff_tab.refresh_users_table()
        self.staff_tab.refresh_prof_dropdown()
