import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from auth import LoginWindow
from processor import DataProcessor

class StudentManagementSystem:
    def __init__(self, root, current_user):
        self.root = root
        self.current_user = current_user
        self.root.title(f"Manager Pro - User: {self.current_user}")
        self.root.geometry("1200x700")

        self.db = Database()
        self.engine = DataProcessor(self.db.conn)

        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        # LEFT: Control Panel
        self.left = tk.Frame(self.root, width=300, padx=20, pady=20, bd=1, relief="solid", bg="#ffffff")
        self.left.pack(side="left", fill="y")

        tk.Label(self.left, text="STUDENT EDITOR", font=("Arial", 12, "bold"), bg="#ffffff").pack(pady=(0,20))

        self.inputs = {}
        fields = [("SAP ID", "sap"), ("Name", "name"), ("Course", "course"),
                  ("Program", "program"), ("Age", "age"), ("Semester", "semester"), ("Email", "email")]

        for label, key in fields:
            tk.Label(self.left, text=label, bg="#ffffff", font=("Arial", 8, "bold")).pack(anchor="w")
            self.inputs[key] = ttk.Entry(self.left)
            self.inputs[key].pack(fill="x", pady=(0, 10))

        # Action Buttons
        ttk.Button(self.left, text="SAVE / UPDATE", command=self.save_record).pack(fill="x", pady=2)
        ttk.Button(self.left, text="DELETE", command=self.delete_record).pack(fill="x", pady=2)
        ttk.Button(self.left, text="EXPORT CSV", command=self.handle_export).pack(fill="x", pady=2)
        ttk.Button(self.left, text="VIEW LOGS", command=self.show_logs).pack(fill="x", pady=2)

        # STATS DISPLAY (Improved)
        tk.Label(self.left, text="--- LIVE STATISTICS ---", bg="#ffffff", font=("Arial", 8, "bold")).pack(pady=(20, 5))
        self.lbl_stats = tk.Label(self.left, text="Loading...", justify="left", fg="#2c3e50", bg="#ecf0f1", padx=10, pady=10, font=("Courier", 10))
        self.lbl_stats.pack(fill="x")

        # RIGHT: Table & Search
        self.right = tk.Frame(self.root, padx=20, pady=20)
        self.right.pack(side="right", fill="both", expand=True)

        search_frame = tk.Frame(self.right)
        search_frame.pack(fill="x", pady=(0, 15))
        self.search_ent = ttk.Entry(search_frame)
        self.search_ent.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(search_frame, text="Search", command=self.handle_search).pack(side="left", padx=2)
        ttk.Button(search_frame, text="Reset", command=self.refresh_table).pack(side="left")

        self.tree = ttk.Treeview(self.right, columns=[f[1] for f in fields], show="headings")
        for label, key in fields:
            self.tree.heading(key, text=label.upper())
            self.tree.column(key, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh_table(self, rows=None):
        for i in self.tree.get_children(): self.tree.delete(i)
        if rows is None:
            self.search_ent.delete(0, tk.END)
            rows = self.db.cursor.execute("SELECT * FROM students").fetchall()

        for r in rows: self.tree.insert("", "end", values=r)

        # UPDATE STATS BOX
        self.lbl_stats.config(text=self.engine.get_stats())

    def handle_search(self):
        query = self.search_ent.get().strip()
        if query: self.refresh_table(self.db.search_students(query))

    def save_record(self):
        gui_data = {k: v.get().strip() for k, v in self.inputs.items()}
        sap = gui_data['sap']
        if len(sap) != 9:
            messagebox.showerror("Error", "SAP ID must be 9 digits")
            return

        existing = self.db.get_student(sap)
        if existing:
            # Smart Merge
            field_order = ["sap", "name", "course", "program", "age", "semester", "email"]
            final = [gui_data[k] if gui_data[k] != "" else existing[i] for i, k in enumerate(field_order)]
            self.db.cursor.execute("UPDATE students SET name=?, course=?, program=?, age=?, semester=?, email=? WHERE sap=?",
                                   (final[1], final[2], final[3], final[4], final[5], final[6], sap))
        else:
            if any(v == "" for v in gui_data.values()):
                messagebox.showwarning("Incomplete", "Fill all fields for new students")
                return
            self.db.cursor.execute("INSERT INTO students VALUES (?,?,?,?,?,?,?)", tuple(gui_data.values()))

        self.db.conn.commit()
        self.refresh_table()
        messagebox.showinfo("Success", "Record Processed")

    def delete_record(self):
        sap = self.inputs['sap'].get().strip()
        if sap and messagebox.askyesno("Confirm", f"Delete {sap}?"):
            self.db.cursor.execute("DELETE FROM students WHERE sap=?", (sap,))
            self.db.conn.commit()
            self.refresh_table()

    def handle_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path: self.engine.export_csv(path); messagebox.showinfo("Done", "Exported")

    def show_logs(self):
        win = tk.Toplevel(self.root)
        t = ttk.Treeview(win, columns=(1,2,3), show="headings")
        t.heading(1, text="Action"); t.heading(2, text="Details"); t.heading(3, text="Time")
        t.pack(fill="both", expand=True)
        for r in self.db.cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC").fetchall():
            t.insert("", "end", values=r)

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        for i, k in enumerate(self.inputs.keys()):
            self.inputs[k].delete(0, tk.END); self.inputs[k].insert(0, vals[i])

def start(user):
    login_root.destroy()
    app_root = tk.Tk()
    StudentManagementSystem(app_root, user)
    app_root.mainloop()

if __name__ == "__main__":
    login_root = tk.Tk()
    LoginWindow(login_root, start)
    login_root.mainloop()
