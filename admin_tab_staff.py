import tkinter as tk
from tkinter import ttk, messagebox
from student_profile import StudentProfileWindow


class StaffTab:
    def __init__(self, parent, db, user, root, engine):
        (
            self.parent,
            self.db,
            self.user,
            self.root,
            self.engine,
        ) = (parent, db, user, root, engine)
        self.setup_ui()
        self.refresh_users_table()

    def setup_ui(self):
        # Line 12-32: UI for creating new staff. Bound to self.create_staff.
        top_frame = tk.Frame(
            self.parent, bg="#ffffff", pady=20, padx=20
        )
        top_frame.pack(fill="x")

        create_frame = tk.LabelFrame(
            top_frame,
            text=" Register New Staff ",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            padx=15,
            pady=15,
        )
        create_frame.pack(
            side="left", fill="y", expand=True, padx=10
        )

        tk.Label(
            create_frame,
            text="Username:",
            bg="#ffffff",
        ).grid(row=0, column=0, sticky="w", pady=5)
        self.u_ent = tk.Entry(create_frame, width=20)
        self.u_ent.grid(row=0, column=1, pady=5)

        tk.Label(
            create_frame,
            text="Password:",
            bg="#ffffff",
        ).grid(row=1, column=0, sticky="w", pady=5)
        self.p_ent = tk.Entry(
            create_frame, show="*", width=20
        )
        self.p_ent.grid(row=1, column=1, pady=5)

        tk.Label(
            create_frame, text="Role:", bg="#ffffff"
        ).grid(row=2, column=0, sticky="w", pady=5)
        self.r_ent = ttk.Combobox(
            create_frame,
            values=["admin", "professor"],
            state="readonly",
            width=17,
        )
        self.r_ent.set("professor")
        self.r_ent.grid(row=2, column=1, pady=5)

        tk.Label(
            create_frame,
            text="Employee ID:",
            bg="#ffffff",
        ).grid(row=3, column=0, sticky="w", pady=5)
        self.eid_ent = tk.Entry(create_frame, width=20)
        self.eid_ent.grid(row=3, column=1, pady=5)

        tk.Button(
            create_frame,
            text="Create Staff Account",
            command=self.create_staff,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
        ).grid(
            row=4, columnspan=2, pady=15, sticky="we"
        )

        # Line 34-53: UI for assigning professors to specific classes.
        assign_frame = tk.LabelFrame(
            top_frame,
            text=" Assign Professor ",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            padx=15,
            pady=15,
        )
        assign_frame.pack(
            side="left", fill="y", expand=True, padx=10
        )

        tk.Label(
            assign_frame,
            text="Professor:",
            bg="#ffffff",
        ).grid(row=0, column=0, sticky="w", pady=2)
        self.asn_prof = ttk.Combobox(
            assign_frame, state="readonly", width=25
        )
        self.asn_prof.grid(row=0, column=1, pady=2)

        tk.Label(
            assign_frame, text="Program:", bg="#ffffff"
        ).grid(row=1, column=0, sticky="w", pady=2)
        self.asn_prog = ttk.Combobox(
            assign_frame,
            values=self.db.programs,
            state="readonly",
            width=25,
        )
        self.asn_prog.grid(row=1, column=1, pady=2)
        self.asn_prog.bind(
            "<<ComboboxSelected>>",
            self.update_assign_course,
        )

        tk.Label(
            assign_frame, text="Course:", bg="#ffffff"
        ).grid(row=2, column=0, sticky="w", pady=2)
        self.asn_course = ttk.Combobox(
            assign_frame, state="readonly", width=25
        )
        self.asn_course.grid(row=2, column=1, pady=2)

        tk.Label(
            assign_frame,
            text="Semester:",
            bg="#ffffff",
        ).grid(row=3, column=0, sticky="w", pady=2)
        self.asn_sem = ttk.Combobox(
            assign_frame,
            values=[str(i) for i in range(1, 11)],
            state="readonly",
            width=25,
        )
        self.asn_sem.grid(row=3, column=1, pady=2)
        self.asn_sem.bind(
            "<<ComboboxSelected>>",
            self.update_assign_subject,
        )

        tk.Label(
            assign_frame, text="Batch:", bg="#ffffff"
        ).grid(row=4, column=0, sticky="w", pady=2)
        self.asn_batch = ttk.Combobox(
            assign_frame,
            values=["B1", "B2", "B3", "B4", "B5"],
            state="readonly",
            width=25,
        )
        self.asn_batch.grid(row=4, column=1, pady=2)

        tk.Label(
            assign_frame, text="Subject:", bg="#ffffff"
        ).grid(row=5, column=0, sticky="w", pady=2)
        self.asn_subj = ttk.Combobox(
            assign_frame, state="readonly", width=25
        )
        self.asn_subj.grid(row=5, column=1, pady=2)

        tk.Button(
            assign_frame,
            text="Lock Assignment",
            command=self.assign_professor,
            bg="#2980b9",
            fg="white",
            font=("Arial", 10, "bold"),
        ).grid(
            row=6, columnspan=2, pady=10, sticky="we"
        )

        # Line 55-66: The bottom user directory tree.
        bot_frame = tk.Frame(
            self.parent, bg="#ffffff", padx=20, pady=10
        )
        bot_frame.pack(fill="both", expand=True)

        list_bar = tk.Frame(bot_frame, bg="#ffffff")
        list_bar.pack(fill="x", pady=5)

        tk.Label(
            list_bar,
            text="System Directory",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
        ).pack(side="left")
        ttk.Button(
            list_bar,
            text="❌ Delete Selected User",
            command=self.delete_staff,
        ).pack(side="right", padx=5)

        cols = ("Username", "Role", "Linked ID")
        self.user_tree = ttk.Treeview(
            bot_frame, columns=cols, show="headings"
        )
        for c in cols:
            self.user_tree.heading(c, text=c)
        self.user_tree.pack(fill="both", expand=True)
        self.user_tree.bind(
            "<Double-1>", self.open_user_profile
        )

    def create_staff(self):
        u, p, r, eid = (
            self.u_ent.get().strip(),
            self.p_ent.get().strip(),
            self.r_ent.get(),
            self.eid_ent.get().strip(),
        )
        if not u or not p:
            return messagebox.showerror(
                "Error",
                "Username and Password are required.",
            )

        # Line 74-81: Audit log integration for staff creation.
        if self.db.register_user(u, p, r, eid):
            self.db.log_action(
                self.user,
                "ADD_STAFF",
                f"Created {r} account: {u}",
            )
            messagebox.showinfo(
                "Success",
                f"{r.title()} Account Created!",
            )
            self.u_ent.delete(0, tk.END)
            self.p_ent.delete(0, tk.END)
            self.eid_ent.delete(0, tk.END)
            self.refresh_users_table()
        else:
            messagebox.showerror(
                "Error", "Username is already taken."
            )

    def delete_staff(self):
        sel = self.user_tree.selection()
        if not sel:
            return messagebox.showwarning(
                "Warning", "Select a user to delete."
            )

        username, role = (
            self.user_tree.item(sel[0])["values"][0],
            self.user_tree.item(sel[0])["values"][1],
        )

        if username == self.user:
            return messagebox.showerror(
                "Error",
                "You cannot delete your own session.",
            )
        if role == "student":
            return messagebox.showerror(
                "Access Denied",
                "Use Student Management to delete students.",
            )

        # Line 93-96: The Enterprise Velocity Check. If they delete too fast, block the thread.
        logs = self.db.get_recent_logs(self.user, 60)
        if self.engine.check_velocity_lockdown(logs):
            self.db.log_action(
                self.user,
                "SECURITY_FLAG",
                "Triggered staff delete velocity lockdown.",
            )
            return messagebox.showerror(
                "LOCKDOWN",
                "Velocity limit exceeded. Deletes blocked.",
            )

        if messagebox.askyesno(
            "Confirm",
            f"Permanently delete {role} '{username}'?",
        ):
            self.db.delete_user(username)
            self.db.log_action(
                self.user,
                "DELETE_STAFF",
                f"Removed {role}: {username}",
            )
            self.refresh_users_table()

    def update_assign_course(self, event=None):
        self.asn_course.config(
            values=self.db.courses_map.get(
                self.asn_prog.get(), []
            )
        )

    def update_assign_subject(self, event=None):
        prog, course, sem = (
            self.asn_prog.get(),
            self.asn_course.get(),
            self.asn_sem.get(),
        )
        if prog and course and sem:
            self.asn_subj.config(
                values=self.db.get_curriculum(
                    prog, course, int(sem)
                )
            )

    def assign_professor(self):
        prof, prog, course, sem, batch, subj = (
            self.asn_prof.get(),
            self.asn_prog.get(),
            self.asn_course.get(),
            self.asn_sem.get(),
            self.asn_batch.get(),
            self.asn_subj.get(),
        )

        if not all(
            [prof, prog, course, sem, batch, subj]
        ):
            return messagebox.showerror(
                "Error", "Fill all assignment fields."
            )

        # Line 116-121: Call SQLite, then hit the audit log if successful.
        success, msg = self.db.assign_professor(
            prof, prog, course, int(sem), batch, subj
        )
        if success:
            self.db.log_action(
                self.user,
                "ASSIGN_PROF",
                f"Assigned {prof} to {subj} ({batch})",
            )
            messagebox.showinfo("Assigned", msg)
        else:
            messagebox.showerror("Error", msg)

    def refresh_users_table(self):
        # Line 124-131: Table wipe, fetch, zebra striping mathematically applied.
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        users = self.db.cursor.execute(
            "SELECT username, role, linked_id FROM users"
        ).fetchall()
        for i, u in enumerate(users):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.user_tree.insert(
                "", "end", values=u, tags=(tag,)
            )
        self.user_tree.tag_configure(
            "oddrow", background="#f2f2f2"
        )
        self.user_tree.tag_configure(
            "evenrow", background="#ffffff"
        )
        self.refresh_prof_dropdown()

    def refresh_prof_dropdown(self):
        profs = self.db.cursor.execute(
            "SELECT username FROM users WHERE role='professor'"
        ).fetchall()
        self.asn_prof.config(
            values=[p[0] for p in profs]
        )

    def open_user_profile(self, event):
        sel = self.user_tree.selection()
        if not sel:
            return
        vals = self.user_tree.item(sel[0])["values"]
        if vals[1] == "student":
            StudentProfileWindow(
                self.root,
                self.db,
                self.engine,
                str(vals[2]),
            )
