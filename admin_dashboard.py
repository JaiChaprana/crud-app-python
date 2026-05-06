import tkinter as tk
from tkinter import ttk, messagebox


class CurriculumDashboard:
    def __init__(self, parent, db):
        # Line 6: Ingest the database singleton.
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title(
            "Curriculum Management Engine"
        )
        self.window.geometry("950x650")
        self.window.configure(bg="#ffffff")
        self.window.grab_set()
        self.setup_ui()

    def setup_ui(self):
        # Line 16: Strict #2c3e50 UI styling.
        header = tk.Label(
            self.window,
            text="Global Curriculum Engine",
            font=("Segoe UI", 16, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=15,
        )
        header.pack(fill="x")

        input_frame = tk.LabelFrame(
            self.window,
            text="Define New Subject Mapping",
            bg="#ffffff",
            font=("Arial", 10, "bold"),
        )
        input_frame.pack(fill="x", padx=15, pady=15)

        tk.Label(
            input_frame, text="Program:", bg="#ffffff"
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=15,
            sticky="e",
        )
        self.prog_ent = ttk.Combobox(
            input_frame,
            values=self.db.programs,
            state="readonly",
            width=12,
        )
        self.prog_ent.grid(
            row=0, column=1, padx=5, pady=15
        )
        self.prog_ent.bind(
            "<<ComboboxSelected>>",
            self.update_course_dropdown,
        )

        tk.Label(
            input_frame, text="Course:", bg="#ffffff"
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=15,
            sticky="e",
        )
        self.crs_ent = ttk.Combobox(
            input_frame, state="readonly", width=15
        )
        self.crs_ent.grid(
            row=0, column=3, padx=5, pady=15
        )

        tk.Label(
            input_frame, text="Sem:", bg="#ffffff"
        ).grid(
            row=0,
            column=4,
            padx=5,
            pady=15,
            sticky="e",
        )
        self.sem_ent = ttk.Combobox(
            input_frame,
            values=[str(i) for i in range(1, 9)],
            state="readonly",
            width=4,
        )
        self.sem_ent.grid(
            row=0, column=5, padx=5, pady=15
        )

        tk.Label(
            input_frame, text="Subject:", bg="#ffffff"
        ).grid(
            row=0,
            column=6,
            padx=5,
            pady=15,
            sticky="e",
        )
        self.sub_ent = ttk.Entry(input_frame, width=18)
        self.sub_ent.grid(
            row=0, column=7, padx=5, pady=15
        )

        tk.Label(
            input_frame, text="Credits:", bg="#ffffff"
        ).grid(
            row=0,
            column=8,
            padx=5,
            pady=15,
            sticky="e",
        )
        self.cred_ent = ttk.Combobox(
            input_frame,
            values=[str(i) for i in range(1, 6)],
            state="readonly",
            width=4,
        )
        self.cred_ent.grid(
            row=0, column=9, padx=5, pady=15
        )

        ttk.Button(
            input_frame,
            text="Add",
            command=self.save_mapping,
        ).grid(row=0, column=10, padx=10, pady=15)

        cols = (
            "Program",
            "Course",
            "Semester",
            "Subject",
            "Credits",
        )
        self.tree = ttk.Treeview(
            self.window, columns=cols, show="headings"
        )
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15),
        )

        btn_frame = tk.Frame(self.window, bg="#ffffff")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        ttk.Button(
            btn_frame,
            text="Delete Selected Mapping",
            command=self.delete_mapping,
        ).pack(side="right")

        self.refresh_table()

    def update_course_dropdown(self, event=None):
        prog = self.prog_ent.get()
        courses = self.db.courses_map.get(
            prog, ["General"]
        )
        self.crs_ent.config(values=courses)
        if courses:
            self.crs_ent.set(courses[0])
        else:
            self.crs_ent.set("")

    def save_mapping(self):
        # Line 64-68: Grab and strip all string variables.
        prog, crs, sem_str, sub, cred_str = (
            self.prog_ent.get().strip(),
            self.crs_ent.get().strip(),
            self.sem_ent.get().strip(),
            self.sub_ent.get().strip(),
            self.cred_ent.get().strip(),
        )

        if not all(
            [prog, crs, sem_str, sub, cred_str]
        ):
            return messagebox.showwarning(
                "Incomplete",
                "All fields are required.",
            )

        # Line 71: Pass cleanly casted integers to the DB engine.
        if self.db.add_curriculum_subject(
            prog, crs, int(sem_str), sub, int(cred_str)
        ):
            self.sub_ent.delete(0, tk.END)
            self.cred_ent.set("")
            self.refresh_table()
        else:
            messagebox.showerror(
                "Duplicate",
                "Subject already exists for this program.",
            )

    def delete_mapping(self):
        selected = self.tree.selection()
        if not selected:
            return messagebox.showwarning(
                "Warning", "Select a mapping."
            )

        # Line 81: Unpack the selected Treeview values.
        item = self.tree.item(selected[0])
        prog, crs, sem, sub, _ = item["values"]

        if messagebox.askyesno(
            "Confirm", f"Remove '{sub}' from {prog}?"
        ):
            self.db.delete_curriculum_subject(
                prog, crs, sem, sub
            )
            self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        data = self.db.get_all_curriculum()
        for i, r in enumerate(data):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert(
                "", "end", values=r, tags=(tag,)
            )
        self.tree.tag_configure(
            "oddrow", background="#f2f2f2"
        )
        self.tree.tag_configure(
            "evenrow", background="#ffffff"
        )
