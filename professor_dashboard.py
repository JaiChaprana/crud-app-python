import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

class ProfessorApp:
    def __init__(self, root, username, linked_id, db, engine):
        self.root = root
        self.user = username
        self.linked_id = linked_id

        # Dependency Injection: Ingest our core engines
        self.db = db
        self.engine = engine

        self.root.title(f"Professor Portal | User: {self.user}")
        self.root.geometry("1100x650")
        self.root.configure(bg="#f4f6f9")

        # Fetch the batches this specific professor is authorized to grade
        self.assignments = self.db.get_professor_batches(self.user)

        # Mathematical constraints for the 30/20/50 split
        self.max_limits = {
            "mid_sem": 20.0,
            "end_sem": 30.0,
            "ct_1": 15.0,
            "ct_2": 15.0,
            "quiz_1": 10.0,
            "quiz_2": 10.0
        }

        self.setup_ui()

    def setup_ui(self):
        # --- HEADER & CLASS SELECTOR ---
        top = tk.Frame(self.root, bg="#2c3e50", pady=15, padx=20)
        top.pack(fill="x")

        tk.Label(top, text="Grading Engine", font=("Segoe UI", 16, "bold"), bg="#2c3e50", fg="white").pack(side="left")

        # Control Panel
        ctrl = tk.Frame(self.root, bg="#ffffff", pady=15, padx=20, bd=1, relief="solid")
        ctrl.pack(fill="x", padx=20, pady=15)

        tk.Label(ctrl, text="Select Class:", font=("Arial", 10, "bold"), bg="#ffffff").pack(side="left")

        assign_strs = [f"{a[0]} | {a[1]} | Sem {a[2]} | {a[3]} | {a[4]}" for a in self.assignments]
        self.class_combo = ttk.Combobox(ctrl, values=assign_strs, state="readonly", width=40)
        if assign_strs: self.class_combo.set(assign_strs[0])
        self.class_combo.pack(side="left", padx=10)

        tk.Label(ctrl, text="Component:", font=("Arial", 10, "bold"), bg="#ffffff").pack(side="left", padx=(20,0))
        self.comp_combo = ttk.Combobox(ctrl, values=list(self.max_limits.keys()), state="readonly")
        self.comp_combo.set("mid_sem")
        self.comp_combo.pack(side="left", padx=10)

        ttk.Button(ctrl, text="Load Roster", command=self.load_roster).pack(side="left", padx=10)

        # --- DATA TABLE ---
        mid_frame = tk.Frame(self.root, bg="#f4f6f9")
        mid_frame.pack(fill="both", expand=True, padx=20)

        cols = ("SAP ID", "Name", "Current Marks")
        self.tree = ttk.Treeview(mid_frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")

        self.tree.tag_configure('oddrow', background='#f2f2f2')
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # --- ACTION FOOTER ---
        bot = tk.Frame(self.root, bg="#ffffff", pady=15, padx=20, bd=1, relief="solid")
        bot.pack(fill="x", side="bottom", padx=20, pady=20)

        tk.Label(bot, text="Selected SAP:", bg="#ffffff", font=("Arial", 10, "bold")).pack(side="left")
        self.sap_ent = tk.Entry(bot, state="readonly", width=15)
        self.sap_ent.pack(side="left", padx=10)

        tk.Label(bot, text="Marks:", bg="#ffffff", font=("Arial", 10, "bold")).pack(side="left")
        self.marks_ent = tk.Entry(bot, width=10)
        self.marks_ent.pack(side="left", padx=10)

        tk.Button(bot, text="Update Mark", command=self.update_mark, bg="#2980b9", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        ttk.Button(bot, text="Download Template (CSV)", command=self.download_template).pack(side="right", padx=10)
        tk.Button(bot, text="Bulk Import Marks (CSV)", command=self.bulk_import, bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(side="right", padx=10)

    def load_roster(self):
        sel = self.class_combo.get()
        if not sel: return
        parts = [p.strip() for p in sel.split("|")]
        prog, course, sem, batch, subj = parts[0], parts[1], parts[2].replace("Sem ",""), parts[3], parts[4]
        comp = self.comp_combo.get()

        for item in self.tree.get_children(): self.tree.delete(item)

        students = self.db.cursor.execute("SELECT sap, name FROM students WHERE program=? AND course=? AND semester=? AND batch=?", (prog, course, sem, batch)).fetchall()

        for i, (sap, name) in enumerate(students):
            mark = 0.0
            grade_row = self.db.cursor.execute("SELECT * FROM grades_detailed WHERE sap=? AND semester=? AND subject=?", (sap, sem, subj)).fetchone()
            if grade_row:
                comp_idx = {"mid_sem":3, "end_sem":4, "ct_1":5, "ct_2":6, "quiz_1":7, "quiz_2":8}[comp]
                mark = grade_row[comp_idx]

            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=(sap, name, mark), tags=(tag,))

    def on_select(self, e):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0])['values']
            self.sap_ent.configure(state="normal")
            self.sap_ent.delete(0, tk.END)
            self.sap_ent.insert(0, vals[0])
            self.sap_ent.configure(state="readonly")

            self.marks_ent.delete(0, tk.END)
            self.marks_ent.insert(0, vals[2])

    def update_mark(self):
        sap = self.sap_ent.get()
        marks = self.marks_ent.get()
        if not sap or not marks: return

        sel = self.class_combo.get()
        parts = [p.strip() for p in sel.split("|")]
        sem, subj = parts[2].replace("Sem ",""), parts[4]
        comp = self.comp_combo.get()

        try:
            val = float(marks)

            # Mathematical bounds checking: 0 <= X <= Max_Limit
            if val < 0:
                messagebox.showerror("Validation Error", "Marks cannot be negative.")
                return
            if val > self.max_limits[comp]:
                messagebox.showerror("Validation Error", f"Maximum marks for {comp} is {self.max_limits[comp]}.\nYou entered {val}.")
                return

            self.db.update_detailed_grade(sap, sem, subj, comp, val)
            self.db.log_action(self.user, "GRADE_UPDATE", f"Updated {comp} for SAP {sap} in {subj}")
            self.load_roster()
            self.marks_ent.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Marks must be a valid number.")

    def download_template(self):
        sel = self.class_combo.get()
        if not sel: return messagebox.showwarning("Warning", "Select a class first.")

        parts = [p.strip() for p in sel.split("|")]
        prog, course, sem, batch, subj = parts[0], parts[1], parts[2].replace("Sem ",""), parts[3], parts[4]

        students = self.db.cursor.execute("SELECT sap, name FROM students WHERE program=? AND course=? AND semester=? AND batch=?", (prog, course, sem, batch)).fetchall()
        if not students: return messagebox.showinfo("Empty", "No students found in this batch.")

        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"Marks_{batch}_{subj}.csv", filetypes=[("CSV Files", "*.csv")])
        if path:
            df = pd.DataFrame(students, columns=["sap", "name"])
            for comp in self.max_limits.keys(): df[comp] = 0.0
            df.to_csv(path, index=False)
            messagebox.showinfo("Success", "Template downloaded.")

    def bulk_import(self):
        sel = self.class_combo.get()
        if not sel: return messagebox.showwarning("Warning", "Select a class first.")

        parts = [p.strip() for p in sel.split("|")]
        sem, subj = parts[2].replace("Sem ",""), parts[4]

        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            try:
                df = pd.read_csv(path)
                required_cols = ["sap"] + list(self.max_limits.keys())
                if not all(col in df.columns for col in required_cols):
                    return messagebox.showerror("Error", "CSV is missing required grading columns.")

                # Strict Validation Pass (Vectorized bounds checking via Pandas could be used, but iteration guarantees safe rollbacks)
                for _, row in df.iterrows():
                    sap = str(row["sap"])
                    for comp, limit in self.max_limits.items():
                        val = float(row[comp])
                        if val < 0 or val > limit:
                            raise ValueError(f"SAP {sap} has invalid marks for {comp}: {val}. Limit is {limit}.")

                # Insertion Pass
                for _, row in df.iterrows():
                    sap = str(row["sap"])
                    for comp in self.max_limits.keys():
                        self.db.update_detailed_grade(sap, sem, subj, comp, float(row[comp]))

                self.load_roster()
                self.db.log_action(self.user, "BULK_MARKS_UPLOAD", f"Imported marks for {subj} (Sem {sem})")
                messagebox.showinfo("Success", "Marks imported successfully.")
            except ValueError as ve:
                messagebox.showerror("Validation Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {str(e)}")
