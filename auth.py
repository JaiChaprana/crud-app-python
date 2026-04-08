import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.title("System Authentication")
        self.root.geometry("350x450")
        self.root.configure(bg="#ffffff")

        # Multi-user DB (Case-insensitive lookup)
        self.users_db = {"jai": "123", "a sai rao": "1234", "admin": "12345"}

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="STUDENT SYSTEM", font=("Segoe UI", 16, "bold"), bg="#ffffff").pack(pady=(40, 30))

        tk.Label(self.root, text="Username", bg="#ffffff").pack(anchor="w", padx=50)
        self.user_ent = ttk.Entry(self.root)
        self.user_ent.pack(fill="x", padx=50, pady=(0, 15))

        tk.Label(self.root, text="Password", bg="#ffffff").pack(anchor="w", padx=50)
        self.pass_ent = ttk.Entry(self.root, show="*")
        self.pass_ent.pack(fill="x", padx=50, pady=(0, 30))

        ttk.Button(self.root, text="LOGIN", command=self.check_auth).pack(fill="x", padx=50)
        self.root.bind('<Return>', lambda e: self.check_auth())

    def check_auth(self):
        u_raw = self.user_ent.get().strip()
        p = self.pass_ent.get().strip()

        if u_raw.lower() in self.users_db and self.users_db[u_raw.lower()] == p:
            self.on_success(u_raw)
        else:
            messagebox.showerror("Auth Failed", "Invalid credentials!")
