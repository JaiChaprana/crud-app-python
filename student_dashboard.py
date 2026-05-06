import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)


class StudentDashboard:
    """Read-Only Analytics Portal for Students"""

    def __init__(
        self, root, username, linked_id, db, engine
    ):
        self.root = root
        self.sap = linked_id
        # Ingest the singletons
        self.db = db
        self.engine = engine

        self.root.title(
            f"Student Portal | SAP: {self.sap}"
        )
        self.root.geometry("1100x650")
        self.root.configure(bg="#f4f6f9")

        self.student_info = self.db.get_student(
            self.sap
        )
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # --- HEADER ---
        header_frame = tk.Frame(
            self.root, bg="#2c3e50", pady=15
        )
        header_frame.pack(fill="x")

        name = (
            self.student_info[1]
            if self.student_info
            else "Unknown Student"
        )

        # Calculate Current GPA and Future Trajectory
        sgpa_dict, cgpa, self.grade_records = (
            self.db.calculate_gpa(self.sap)
        )
        proj_sgpa, trend = (
            self.engine.predict_trajectory(sgpa_dict)
        )

        tk.Label(
            header_frame,
            text=f"Welcome {name} | SAP: {self.sap}",
            font=("Segoe UI", 16, "bold"),
            bg="#2c3e50",
            fg="white",
        ).pack(side="top")

        # Inject the Data Science Feature into the UI
        tk.Label(
            header_frame,
            text=f"Current CGPA: {cgpa} | Projected Next SGPA: {proj_sgpa} ({trend} Trend)",
            font=("Arial", 11, "bold"),
            bg="#2c3e50",
            fg="#f1c40f",
        ).pack(side="top", pady=(5, 0))

        ttk.Button(
            header_frame,
            text="Download Marksheet (CSV)",
            command=self.export_csv,
        ).place(relx=0.95, rely=0.5, anchor="e")

        # --- CONTENT AREA (SPLIT LEFT & RIGHT) ---
        content = tk.Frame(self.root, bg="#f4f6f9")
        content.pack(
            fill="both", expand=True, padx=20, pady=20
        )

        # LEFT: Detailed Grades Table
        left_frame = tk.Frame(
            content, bg="#ffffff", bd=1, relief="solid"
        )
        left_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10),
        )

        tk.Label(
            left_frame,
            text="Detailed Subject Breakdown",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
        ).pack(pady=15)

        cols = (
            "Sem",
            "Subject",
            "Total",
            "Credits",
            "Grade",
        )
        self.tree = ttk.Treeview(
            left_frame, columns=cols, show="headings"
        )
        for c in cols:
            self.tree.heading(c, text=c)
            w = 140 if c == "Subject" else 60
            self.tree.column(
                c, width=w, anchor="center"
            )

        # The Tkinter bug fix: pady=(0, 15) instead of bottom=15
        self.tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15),
        )

        # RIGHT: Matplotlib Performance Graph
        self.right_frame = tk.Frame(
            content,
            bg="#ffffff",
            width=400,
            bd=1,
            relief="solid",
        )
        self.right_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(10, 0),
        )

        tk.Label(
            self.right_frame,
            text="SGPA Performance Trend",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
        ).pack(pady=15)

        self.fig, self.ax = plt.subplots(
            figsize=(5, 4), dpi=100
        )
        self.fig.patch.set_facecolor("#ffffff")
        self.canvas = FigureCanvasTkAgg(
            self.fig, master=self.right_frame
        )
        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10),
        )

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Populate table using the cached records from setup_ui
        for i, g in enumerate(self.grade_records):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                "end",
                values=(
                    g["semester"],
                    g["subject"],
                    round(g["total_marks"], 1),
                    g["credits"],
                    g["letter_grade"],
                ),
                tags=(tag,),
            )

        # Draw the Matplotlib Graph
        self.ax.clear()
        sgpa_dict, _, _ = self.db.calculate_gpa(
            self.sap
        )

        if sgpa_dict:
            sems = sorted(list(sgpa_dict.keys()))
            sgpas = [sgpa_dict[s] for s in sems]

            self.ax.plot(
                sems,
                sgpas,
                marker="o",
                linestyle="-",
                color="#e74c3c",
                linewidth=2,
            )
            self.ax.set_ylabel(
                "SGPA", fontweight="bold"
            )
            self.ax.set_xlabel(
                "Semester", fontweight="bold"
            )
            self.ax.set_ylim(0, 10.5)
            self.ax.set_xticks(sems)
            self.ax.grid(
                True, linestyle="--", alpha=0.7
            )
            self.fig.tight_layout()
        else:
            self.ax.text(
                0.5,
                0.5,
                "No Examination Data Available",
                ha="center",
                va="center",
                color="#7f8c8d",
            )
            self.ax.axis("off")

        self.canvas.draw()

    def export_csv(self):
        grades = self.db.get_detailed_grades(self.sap)
        if not grades:
            messagebox.showwarning(
                "No Data",
                "There are no academic records to export yet.",
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"Marksheet_{self.sap}.csv",
            filetypes=[("CSV Files", "*.csv")],
        )
        if path:
            df = pd.DataFrame(grades)
            df["Total_Marks"] = (
                df["mid_sem"]
                + df["end_sem"]
                + df["ct_1"]
                + df["ct_2"]
                + df["quiz_1"]
                + df["quiz_2"]
            )
            df.to_csv(path, index=False)
            messagebox.showinfo(
                "Download Complete",
                "Official marksheet downloaded successfully.",
            )
