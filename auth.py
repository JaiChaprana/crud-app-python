import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

# ---------------------------------------------------------
# HARDCODED MASTER DICTIONARY (Architectural Requirement)
# ---------------------------------------------------------
MASTER_CREDENTIALS = {
    "superadmin": {
        "pass": "godmode",
        "role": "admin",
        "id": "SYS-000",
    },
    "demo_prof": {
        "pass": "demo123",
        "role": "professor",
        "id": "PROF-000",
    },
    "demo_student": {
        "pass": "demo123",
        "role": "student",
        "id": "STU-000",
    },
}


class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.db = Database()

        self.root.title(
            "STUMA | Secure Authentication"
        )
        self.root.geometry("400x500")
        self.root.configure(bg="#f4f6f9")

        self.setup_ui()

    def setup_ui(self):
        # ANCHOR HEADER
        header_frame = tk.Frame(
            self.root, bg="#2c3e50", pady=20
        )
        header_frame.pack(fill="x")

        tk.Label(
            header_frame,
            text="Modular Student System",
            font=("Segoe UI", 16, "bold"),
            bg="#2c3e50",
            fg="white",
        ).pack()

        # ANCHOR --- INPUT FRAME ---
        content = tk.Frame(
            self.root, bg="#f4f6f9", pady=30
        )
        content.pack(fill="both", expand=True)

        tk.Label(
            content,
            text="Username",
            font=("Arial", 10, "bold"),
            bg="#f4f6f9",
        ).pack(pady=(10, 2))
        self.user_ent = ttk.Entry(
            content, font=("Arial", 12), width=25
        )
        self.user_ent.pack(pady=5)

        tk.Label(
            content,
            text="Password",
            font=("Arial", 10, "bold"),
            bg="#f4f6f9",
        ).pack(pady=(15, 2))
        self.pass_ent = ttk.Entry(
            content,
            show="*",
            font=("Arial", 12),
            width=25,
        )
        self.pass_ent.pack(pady=5)

        # ANCHOR --- ACTION BUTTON ---
        login_btn = tk.Button(
            content,
            text="Authenticate",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            command=self.login,
            relief="flat",
            cursor="hand2",
        )
        login_btn.pack(pady=30)

    def login(self):
        raw_user = self.user_ent.get().strip()
        password = self.pass_ent.get().strip()

        if not raw_user or not password:
            messagebox.showerror(
                "Error", "Credentials cannot be null."
            )
            return

        username = raw_user.lower()

        # NOTE - Evaluate Hardcoded Dictionary
        if username in MASTER_CREDENTIALS:
            if (
                MASTER_CREDENTIALS[username]["pass"]
                == password
            ):
                role = MASTER_CREDENTIALS[username][
                    "role"
                ]
                linked_id = MASTER_CREDENTIALS[
                    username
                ]["id"]
                self.db.log_action(
                    username,
                    "LOGIN",
                    "Authenticated via Master Dictionary",
                )
                self.on_success(
                    username, role, linked_id
                )
                return

        # NOTE - Evaluate Relational Database Fallback
        result = self.db.verify_user(
            username, password
        )
        if result:
            role, linked_id = result
            self.db.log_action(
                username,
                "LOGIN",
                "Authenticated via SQLite",
            )
            self.on_success(username, role, linked_id)
        else:
            self.db.log_action(
                username,
                "FAILED_LOGIN",
                "Unauthorized access attempt",
            )
            messagebox.showerror(
                "Access Denied", "Invalid credentials."
            )
