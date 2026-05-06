import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from student_profile import StudentProfileWindow
from admin_dashboard import CurriculumDashboard
from analytics_dashboard import AnalyticsWindow

class StudentTab:
    def __init__(self, parent, db, engine, user, root, on_user_change):
        self.parent = parent
        self.db = db
        self.engine = engine
        self.user = user
        self.root = root
        self.on_user_change = on_user_change

        self.setup_ui()
        self.refresh_table()

    def validate_numeric(self, P):
        return P == "" or P.isdigit()

    def setup_ui(self):
        self.left = tk.Frame(self.parent, width=320, bg="#2c3e50")
        self.left.pack(side="left", fill="y")

        tk.Label(self.left, text="Student Setup", font=("Segoe UI", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=20)

        vcmd_num = (self.root.register(self.validate_numeric), '%P')
        fields = ["SAP ID", "Name", "Program", "Course", "Batch", "Age", "Semester", "Email", "Portal Password"]
        self.inputs = {}

        # --- SMART DEFAULTS ---
        self.prog_var = tk.StringVar()
        self.sem_var = tk.StringVar()
        self.prog_var.trace_add("write", self.apply_smart_defaults)
        self.sem_var.trace_add("write", self.apply_smart_defaults)

        for f in fields:
            tk.Label(self.left, text=f, bg="#2c3e50", fg="white", font=("Arial", 10)).pack(anchor="w", padx=20)
            key = "sap" if f == "SAP ID" else ("password" if f == "Portal Password" else f.lower())

            if f == "Program":
                ent = ttk.Combobox(self.left, values=self.db.programs, state="readonly", textvariable=self.prog_var)
                ent.bind("<<ComboboxSelected>>", self.update_course_dropdown)
            elif f == "Course":
                ent = ttk.Combobox(self.left, state="readonly")
            elif f == "Batch":
                ent = ttk.Combobox(self.left, values=["B1", "B2", "B3", "B4", "B5"], state="readonly")
            elif f in ["SAP ID", "Age", "Semester"]:
                var = self.sem_var if f == "Semester" else None
                ent = ttk.Entry(self.left, validate="key", validatecommand=vcmd_num, textvariable=var)
            elif f == "Portal Password":
                ent = ttk.Entry(self.left, show="*")
            else:
                ent = ttk.Entry(self.left)

            ent.pack(fill="x", padx=20, pady=5)
            self.inputs[key] = ent

        # --- ACTION BUTTONS ---
        btn_frame = tk.Frame(self.left, bg="#2c3e50")
        btn_frame.pack(fill="x", padx=20, pady=15)

        ttk.Button(btn_frame, text="Save / Merge Student", command=self.save_record).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Delete Student", command=self.delete_record).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(fill="x", pady=2)

        tk.Label(btn_frame, text="--- System Setup ---", bg="#2c3e50", fg="#bdc3c7").pack(pady=10)
        ttk.Button(btn_frame, text="Manage Curriculum", command=self.open_curriculum).pack(fill="x", pady=2)

        # RESTORED: The Data Hub UI elements
        tk.Label(btn_frame, text="--- Data Hub ---", bg="#2c3e50", fg="#bdc3c7").pack(pady=10)
        ttk.Button(btn_frame, text="Bulk Import (CSV)", command=self.import_data).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Audit Logs", command=self.show_logs).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="📊 Enterprise Analytics", command=self.open_analytics).pack(fill="x", pady=2)

        # --- RIGHT SIDE: DATA TABLE ---
        self.right = tk.Frame(self.parent, bg="#ffffff")
        self.right.pack(side="right", fill="both", expand=True)

        cols = ("SAP ID", "Name", "Course", "Program", "Batch", "Age", "Semester", "Email")
        self.tree = ttk.Treeview(self.right, columns=cols, show="headings")

        for col in cols:
            self.tree.heading(col, text=col)
            w = 80 if col in ["Age", "Semester", "Batch"] else 150
            self.tree.column(col, anchor="center", width=w)

        self.tree.tag_configure('oddrow', background='#f2f2f2')
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.tag_configure('anomaly', background='#e74c3c', foreground='white')

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.open_profile)

    def apply_smart_defaults(self, *args):
        p = self.prog_var.get().strip()
        s = self.sem_var.get().strip()
        if p and s.isdigit():
            age, batch = self.engine.predict_defaults(p, int(s))
            if not self.inputs['age'].get() and age:
                self.inputs['age'].insert(0, str(age))
            if not self.inputs['batch'].get() and batch:
                self.inputs['batch'].set(batch)

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        records = self.db.get_all_students()
        anomalies = self.engine.get_anomalies()

        for i, r in enumerate(records):
            sap = r[0]
            if sap in anomalies:
                tag = 'anomaly'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=r, tags=(tag,))

    def update_course_dropdown(self, event=None):
        prog = self.inputs['program'].get()
        courses = self.db.courses_map.get(prog, ["General"])
        self.inputs['course'].config(values=courses)
        if event and courses: self.inputs['course'].set(courses[0])

    def save_record(self):
        gui = {k: v.get().strip() for k, v in self.inputs.items() if k != "password"}
        password = self.inputs["password"].get().strip()
        sap = gui.get('sap')

        if len(sap) != 9:
            messagebox.showerror("Validation Error", "SAP ID must be 9 digits.")
            return

        existing = self.db.get_student(sap)
        if existing:
            if self.db.update_student(sap, gui):
                self.db.log_action(self.user, "UPDATE", f"Modified SAP {sap}")
                messagebox.showinfo("Success", "Student Record Updated.")
        else:
            if any(v == "" for v in gui.values()):
                messagebox.showwarning("Incomplete", "All academic fields required for new entries.")
                return
            if not password:
                messagebox.showwarning("Incomplete", "Please assign a Portal Password.")
                return

            self.db.add_student(gui)
            self.db.register_user(username=sap, password=password, role="student", linked_id=sap)
            self.db.log_action(self.user, "ADD", f"New Student {sap}")
            messagebox.showinfo("Success", "New Student & Portal Login Created.")

        self.refresh_table()
        self.on_user_change()

    def delete_record(self):
        sap = self.inputs['sap'].get().strip()
        if not sap: return

        logs = self.db.get_recent_logs(self.user, 60)
        if self.engine.check_velocity_lockdown(logs):
            messagebox.showerror("SECURITY LOCKDOWN", "Velocity limit exceeded. Multiple deletes blocked.")
            self.db.log_action(self.user, "SECURITY_FLAG", "Triggered delete velocity lockdown.")
            return

        if messagebox.askyesno("Confirm", f"Delete SAP {sap} permanently?"):
            self.db.delete_student(sap)
            self.db.log_action(self.user, "DELETE", f"Removed SAP {sap}.")
            self.clear_form()
            self.refresh_table()
            self.on_user_change()

    def clear_form(self):
        for ent in self.inputs.values():
            if isinstance(ent, ttk.Combobox): ent.set('')
            else: ent.delete(0, tk.END)

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        self.inputs['program'].set(vals[3])
        self.update_course_dropdown()
        for i, k in enumerate(["sap", "name", "course", "program", "batch", "age", "semester", "email"]):
            widget = self.inputs[k]
            if isinstance(widget, ttk.Combobox): widget.set(vals[i])
            else:
                widget.delete(0, tk.END)
                widget.insert(0, vals[i])

    def open_profile(self, event):
        sel = self.tree.selection()
        if sel:
            sap = str(self.tree.item(sel[0])['values'][0])
            StudentProfileWindow(self.root, self.db, self.engine, sap)

    def open_curriculum(self):
        CurriculumDashboard(self.root, self.db)

    # --- RESTORED METHODS ---

    def import_data(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            success, msg = self.engine.import_csv(path, self.db, self.user)
            self.refresh_table()
            messagebox.showinfo("Import", msg)

    def show_logs(self):
        log_win = tk.Toplevel(self.root)
        log_win.title("System Audit Logs")
        log_win.geometry("750x450")
        log_win.configure(bg="#f4f6f9")

        tk.Label(log_win, text="System Audit Logs", font=("Segoe UI", 14, "bold"), bg="#f4f6f9").pack(pady=10)

        # We fetch columns matching our updated 4-column SQLite logs table setup
        cols = ("Action", "Details", "Timestamp", "User")
        tree = ttk.Treeview(log_win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            w = 120 if c in ["Action", "User"] else (150 if c == "Timestamp" else 300)
            tree.column(c, anchor="center", width=w)

        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for r in self.db.cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC"):
            tree.insert("", "end", values=r)

    def open_analytics(self):
        AnalyticsWindow(self.root, self.engine)
