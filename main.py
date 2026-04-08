import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from auth import LoginWindow
from processor import DataProcessor


class StudentApp:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"Student Manager Pro - {self.user}")
        self.root.geometry("1200x750")

        self.db = Database()
        self.engine = DataProcessor(self.db.conn)

        self.setup_styles()
        self.setup_ui()
        self.refresh_table()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Professional Header Styling
        style.configure(
            "Treeview.Heading",
            background="#2c3e50",
            foreground="white",
            font=("Arial", 10, "bold"),
            padding=5,
        )

        # Row styling
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.map("Treeview", background=[('selected', '#3498db')])

    def setup_ui(self):
        # Sidebar
        self.left = tk.Frame(
            self.root, width=320, bg="#ffffff", padx=20, pady=20, bd=1, relief="solid"
        )
        self.left.pack(side="left", fill="y")

        self.inputs = {}
        fields = [
            ("SAP ID", "sap"),
            ("Name", "name"),
            ("Course", "course"),
            ("Program", "program"),
            ("Age", "age"),
            ("Semester", "semester"),
            ("Email", "email"),
        ]

        for label, key in fields:
            tk.Label(self.left, text=label, bg="#ffffff", font=("Arial", 8, "bold")).pack(
                anchor="w"
            )
            self.inputs[key] = ttk.Entry(self.left)
            self.inputs[key].pack(fill="x", pady=(0, 10))

        ttk.Button(self.left, text="SAVE / SMART UPDATE", command=self.save_record).pack(
            fill="x", pady=5
        )
        ttk.Button(self.left, text="DELETE RECORD", command=self.delete_record).pack(
            fill="x", pady=2
        )
        ttk.Button(self.left, text="EXPORT TO CSV", command=self.export).pack(
            fill="x", pady=2
        )

        self.stats_box = tk.Label(
            self.left,
            text="",
            bg="#ecf0f1",
            justify="left",
            font=("Courier", 10),
            padx=10,
            pady=10,
        )
        self.stats_box.pack(fill="x", pady=20)

        # Right Side (Table)
        self.right = tk.Frame(self.root, padx=20, pady=20)
        self.right.pack(side="right", fill="both", expand=True)

        search_f = tk.Frame(self.right)
        search_f.pack(fill="x", pady=(0, 15))
        self.s_ent = ttk.Entry(search_f)
        self.s_ent.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(search_f, text="Search", command=self.search).pack(side="left", padx=2)
        ttk.Button(search_f, text="Reset", command=self.refresh_table).pack(side="left")

        self.tree = ttk.Treeview(
            self.right, columns=[f[1] for f in fields], show="headings"
        )
        for label, key in fields:
            self.tree.heading(key, text=label.upper())
            self.tree.column(key, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh_table(self, rows=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if rows is None:
            self.s_ent.delete(0, tk.END)
            rows = self.db.cursor.execute("SELECT * FROM students").fetchall()
        for r in rows:
            self.tree.insert("", "end", values=r)
        self.stats_box.config(text=self.engine.get_stats())

    def save_record(self):
        gui = {k: v.get().strip() for k, v in self.inputs.items()}
        if len(gui['sap']) != 9:
            messagebox.showerror("Error", "SAP ID must be 9 digits")
            return

        existing = self.db.get_student(gui['sap'])
        if existing:
            # SMART MERGE: Keep old if new is blank
            f_order = ["sap", "name", "course", "program", "age", "semester", "email"]
            final = [
                gui[k] if gui[k] != "" else existing[i] for i, k in enumerate(f_order)
            ]
            self.db.cursor.execute(
                "UPDATE students SET name=?, course=?, program=?, age=?, semester=?, email=? WHERE sap=?",
                (final[1], final[2], final[3], final[4], final[5], final[6], gui['sap']),
            )
            self.db.log_action(self.user, "UPDATE", f"Modified SAP {gui['sap']}")
        else:
            if any(v == "" for v in gui.values()):
                messagebox.showwarning("Incomplete", "Fill all fields for new students")
                return
            self.db.cursor.execute(
                "INSERT INTO students VALUES (?,?,?,?,?,?,?)", tuple(gui.values())
            )
            self.db.log_action(self.user, "ADD", f"New Student {gui['sap']}")

        self.db.conn.commit()
        self.refresh_table()
        messagebox.showinfo("Success", "Data Synchronized")

    def delete_record(self):
        sap = self.inputs['sap'].get().strip()
        if sap and messagebox.askyesno("Confirm", f"Delete SAP {sap}?"):
            self.db.cursor.execute("DELETE FROM students WHERE sap=?", (sap,))
            self.db.conn.commit()
            self.db.log_action(self.user, "DELETE", f"Removed {sap}")
            self.refresh_table()

    def search(self):
        q = self.s_ent.get().strip()
        if q:
            self.refresh_table(self.db.search_students(q))

    def export(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            self.engine.export_csv(path)
            messagebox.showinfo("Done", "Exported")

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])['values']
        for i, k in enumerate(self.inputs.keys()):
            self.inputs[k].delete(0, tk.END)
            self.inputs[k].insert(0, vals[i])


def start(user):
    login_root.destroy()
    app_root = tk.Tk()
    StudentApp(app_root, user)
    app_root.mainloop()


if __name__ == "__main__":
    login_root = tk.Tk()
    LoginWindow(login_root, start)
    login_root.mainloop()
