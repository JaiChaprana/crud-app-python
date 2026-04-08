import sqlite3
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# ==========================================
# 1. UPDATED LOGIN SYSTEM (Multi-User)
# ==========================================
class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.title("System Auth")
        self.root.geometry("350x450")
        self.root.configure(bg="#ffffff")

        # MULTI-USER DATA
        # We use a dictionary for easy 'Username: Password' mapping
        self.users_db = {
            "jai": "123",
            "A Sai Rao": "1234",
            "admin": "12345"
        }

        # UI Layout
        tk.Label(root, text="STUDENT SYSTEM", font=("Segoe UI", 16, "bold"), bg="#ffffff").pack(pady=(40, 10))
        tk.Label(root, text="Secure Login", font=("Segoe UI", 10), bg="#ffffff", fg="gray").pack(pady=(0, 30))

        tk.Label(root, text="Username", bg="#ffffff", font=("Segoe UI", 9)).pack(anchor="w", padx=50)
        self.user_ent = ttk.Entry(root)
        self.user_ent.pack(fill="x", padx=50, pady=(0, 15))

        tk.Label(root, text="Password", bg="#ffffff", font=("Segoe UI", 9)).pack(anchor="w", padx=50)
        self.pass_ent = ttk.Entry(root, show="*")
        self.pass_ent.pack(fill="x", padx=50, pady=(0, 30))

        btn = ttk.Button(root, text="LOGIN", command=self.check_auth)
        btn.pack(fill="x", padx=50, pady=5)

        # Bind the 'Enter' key to login for convenience
        self.root.bind('<Return>', lambda event: self.check_auth())

    def check_auth(self):
        u = self.user_ent.get().strip()
        p = self.pass_ent.get().strip()
        # Check if username exists and password matches
        if u in self.users_db and self.users_db[u] == p:
            self.on_success(u) # Pass the username to the main app for logging
        else:
            messagebox.showerror("Auth Failed", "Invalid Username or Password!")

# ==========================================
# 2. MAIN APPLICATION
# ==========================================
class StudentManagementSystem:
    def __init__(self, root, current_user):
        self.root = root
        self.current_user = current_user # Store who logged in
        self.root.title(f"Student Manager Pro - Logged in as: {self.current_user}")
        self.root.geometry("1300x700")
        self.root.configure(bg="#f4f7f6")

        self.db_path = "student_system.db"
        self.init_db()
        self.setup_styles()
        self.create_widgets()
        self.refresh_table()

        # Log the login event
        self.log_action("LOGIN", f"User '{self.current_user}' accessed the system")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                                sap TEXT PRIMARY KEY, name TEXT, course TEXT,
                                program TEXT, age INTEGER, semester INTEGER, email TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                                action TEXT, details TEXT, timestamp TEXT)''')
        self.conn.commit()

    def log_action(self, action, details):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Include the user in the log details
        full_details = f"[{self.current_user}] {details}"
        self.cursor.execute("INSERT INTO logs VALUES (?, ?, ?)", (action, full_details, timestamp))
        self.conn.commit()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", rowheight=30, font=('Segoe UI', 10))
        self.style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))

    def create_widgets(self):
        # LEFT PANEL
        form_frame = tk.Frame(self.root, bg="#ffffff", padx=25, pady=25, borderwidth=1, relief="solid")
        form_frame.pack(side="left", fill="y", padx=20, pady=20)

        tk.Label(form_frame, text="STUDENT EDITOR", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(pady=(0, 10))
        self.lbl_status = tk.Label(form_frame, text="Mode: Adding New", fg="#0056b3", bg="#ffffff", font=("Segoe UI", 9, "italic"))
        self.lbl_status.pack(pady=(0, 15))

        self.inputs = {}
        fields = [("SAP ID", "sap"), ("Full Name", "name"), ("Course", "course"),
                  ("Program", "program"), ("Age", "age"), ("Semester", "semester"), ("Email", "email")]

        for label, key in fields:
            tk.Label(form_frame, text=label, bg="#ffffff", font=("Segoe UI", 9, "bold")).pack(anchor="w")
            ent = ttk.Entry(form_frame)
            ent.pack(fill="x", pady=(0, 10))
            self.inputs[key] = ent

        ttk.Button(form_frame, text="SAVE / UPDATE", command=self.save_record).pack(fill="x", pady=5)
        ttk.Button(form_frame, text="CLEAR FORM", command=self.clear_form).pack(fill="x", pady=5)

        tk.Label(form_frame, text="DATA EXCHANGE", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(pady=(20, 5))
        ttk.Button(form_frame, text="IMPORT CSV", command=self.import_csv).pack(fill="x", pady=2)
        ttk.Button(form_frame, text="EXPORT CSV", command=self.export_csv).pack(fill="x", pady=2)
        ttk.Button(form_frame, text="VIEW AUDIT LOGS", command=self.show_audit_logs).pack(fill="x", pady=(15, 0))

        # RIGHT PANEL
        right_frame = tk.Frame(self.root, bg="#f4f7f6", padx=20, pady=20)
        right_frame.pack(side="right", fill="both", expand=True)

        search_frame = tk.Frame(right_frame, bg="#f4f7f6")
        search_frame.pack(fill="x", pady=(0, 15))
        self.search_ent = ttk.Entry(search_frame)
        self.search_ent.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(search_frame, text="Search", command=self.search_data).pack(side="left")
        ttk.Button(search_frame, text="Delete Selected", command=self.delete_record).pack(side="left", padx=5)

        cols = ("sap", "name", "course", "program", "age", "semester", "email")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)

        footer = tk.Frame(right_frame, bg="#f4f7f6")
        footer.pack(fill="x", pady=(15, 0))
        self.lbl_count = tk.Label(footer, text="Records: 0", font=("Segoe UI", 10, "bold"), bg="#f4f7f6")
        self.lbl_count.pack(side="left")
        ttk.Button(footer, text="Run Analytics", command=self.show_stats).pack(side="right")

    # --- CSV & AUDIT LOGIC ---
    def export_csv(self):
        try:
            df = pd.read_sql_query("SELECT * FROM students", self.conn)
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Export Success", f"Saved to {file_path}")
                self.log_action("EXPORT", f"Exported {len(df)} records")
        except Exception as e: messagebox.showerror("Error", str(e))

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path: return
        try:
            df = pd.read_csv(file_path)
            req = ["sap", "name", "course", "program", "age", "semester", "email"]
            if not all(c in df.columns for c in req):
                messagebox.showerror("Error", "Invalid CSV Headers")
                return
            for _, row in df.iterrows():
                self.cursor.execute("INSERT OR REPLACE INTO students VALUES (?,?,?,?,?,?,?)", tuple(row[req]))
            self.conn.commit()
            self.refresh_table()
            self.log_action("IMPORT", f"Imported from {file_path}")
            messagebox.showinfo("Success", "Import Complete")
        except Exception as e: messagebox.showerror("Error", str(e))

    def show_audit_logs(self):
        audit_win = tk.Toplevel(self.root)
        audit_win.title("System Audit Logs")
        audit_win.geometry("700x400")
        cols = ("Action", "User & Details", "Timestamp")
        tree = ttk.Treeview(audit_win, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=200 if col=="User & Details" else 150)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        for row in self.cursor.fetchall(): tree.insert("", "end", values=row)

    # --- CRUD LOGIC ---
    def refresh_table(self, data=None):
        for item in self.tree.get_children(): self.tree.delete(item)
        if data is None:
            self.cursor.execute("SELECT * FROM students")
            data = self.cursor.fetchall()
        for row in data: self.tree.insert("", "end", values=row)
        self.cursor.execute("SELECT COUNT(*) FROM students")
        self.lbl_count.config(text=f"Total: {self.cursor.fetchone()[0]}")

    def save_record(self):
        d = {k: v.get().strip() for k, v in self.inputs.items()}
        if not (d['sap'].isdigit() and len(d['sap']) == 9):
            messagebox.showerror("Error", "SAP ID must be 9 digits.")
            return
        self.cursor.execute("INSERT OR REPLACE INTO students VALUES (?,?,?,?,?,?,?)", tuple(d.values()))
        self.conn.commit()
        self.log_action("SAVE", f"Saved student SAP: {d['sap']}")
        self.refresh_table(); self.clear_form()

    def delete_record(self):
        sap = self.inputs['sap'].get().strip()
        if not sap or not messagebox.askyesno("Confirm", f"Delete {sap}?"): return
        self.cursor.execute("DELETE FROM students WHERE sap=?", (sap,))
        self.conn.commit()
        self.log_action("DELETE", f"Removed SAP: {sap}")
        self.refresh_table(); self.clear_form()

    def search_data(self):
        q = self.search_ent.get().strip()
        self.cursor.execute("SELECT * FROM students WHERE name LIKE ? OR sap LIKE ?", (f'%{q}%', f'%{q}%'))
        self.refresh_table(self.cursor.fetchall())

    def show_stats(self):
        df = pd.read_sql_query("SELECT age, semester FROM students", self.conn)
        if not df.empty:
            msg = f"Avg Age: {np.mean(df['age']):.1f}\nCommon Sem: {df['semester'].mode()[0]}"
            messagebox.showinfo("Stats", msg)

    def load_selected(self, e):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        for i, key in enumerate(self.inputs.keys()):
            self.inputs[key].delete(0, tk.END); self.inputs[key].insert(0, vals[i])
        self.lbl_status.config(text=f"Editing: {vals[1]}", fg="red")

    def clear_form(self):
        for ent in self.inputs.values(): ent.delete(0, tk.END)
        self.lbl_status.config(text="Mode: Adding New", fg="#0056b3")

    def on_closing(self):
        self.conn.close(); self.root.destroy()

# --- RUNTIME ---
def start_app(username):
    login_root.destroy()
    main_root = tk.Tk()
    app = StudentManagementSystem(main_root, username) # Pass user to main app
    main_root.mainloop()

if __name__ == "__main__":
    login_root = tk.Tk()
    login_screen = LoginWindow(login_root, start_app)
    login_root.mainloop()
