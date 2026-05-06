import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)


class StudentProfileWindow:
    def __init__(self, parent, db, engine, sap):
        # Line 8-10: Dependency Injection. We catch db and engine from the router.
        self.db = db
        self.engine = engine
        self.sap = str(sap)

        self.window = tk.Toplevel(parent)
        self.window.title(
            f"Enterprise Profile - SAP: {self.sap}"
        )
        self.window.geometry("1150x750")
        self.window.configure(bg="#f4f6f9")
        self.window.grab_set()

        self.student_data = self.db.get_student(
            self.sap
        )
        if not self.student_data:
            tk.Label(
                self.window,
                text="Student data not found.",
                font=("Arial", 14),
            ).pack(pady=50)
            return

        # Line 23: Fetch the calculated GPA dictionary safely using the integer-casted logic we built.
        (
            self.sgpa_dict,
            self.cgpa,
            self.grade_records,
        ) = self.db.calculate_gpa(self.sap)
        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.window, bg="#f4f6f9")
        top_frame.pack(fill="x", padx=20, pady=20)

        info_frame = tk.Frame(
            top_frame,
            bg="#ffffff",
            bd=1,
            relief="solid",
            padx=20,
            pady=20,
        )
        info_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10),
        )

        # Line 34-40: We map the raw tuple data from SQLite into readable strings.
        labels = [
            f"Name: {self.student_data[1]}",
            f"SAP ID: {self.student_data[0]}",
            f"Program: {self.student_data[3]}",
            f"Course: {self.student_data[2]}",
            f"Batch: {self.student_data[4]}",
            f"Semester: {self.student_data[6]}",
            f"Age: {self.student_data[5]}",
            f"Email: {self.student_data[7]}",
        ]

        for i, text in enumerate(labels):
            row, col = i // 4, i % 4
            tk.Label(
                info_frame,
                text=text,
                font=("Arial", 10, "bold"),
                bg="#ffffff",
                fg="#2c3e50",
            ).grid(
                row=row,
                column=col,
                padx=10,
                pady=10,
                sticky="w",
            )

        # Line 46-51: The Cumulative Performance dark-mode badge.
        gpa_frame = tk.Frame(
            top_frame,
            bg="#2c3e50",
            bd=1,
            relief="solid",
            padx=20,
            pady=20,
            width=250,
        )
        gpa_frame.pack(
            side="right", fill="y", padx=(10, 0)
        )
        gpa_frame.pack_propagate(False)

        tk.Label(
            gpa_frame,
            text="Cumulative Performance",
            font=("Arial", 11, "bold"),
            bg="#2c3e50",
            fg="#bdc3c7",
        ).pack(pady=(0, 10))
        tk.Label(
            gpa_frame,
            text=f"{self.cgpa}",
            font=("Segoe UI", 36, "bold"),
            bg="#2c3e50",
            fg="#f1c40f",
        ).pack()

        # Line 55: We call NumPy polyfit to predict the next semester's SGPA and print it for the Admin.
        proj_sgpa, trend = (
            self.engine.predict_trajectory(
                self.sgpa_dict
            )
        )
        tk.Label(
            gpa_frame,
            text=f"Proj: {proj_sgpa} ({trend})",
            font=("Arial", 10, "bold"),
            bg="#2c3e50",
            fg="#2ecc71",
        ).pack(pady=(10, 0))

        content = tk.Frame(self.window, bg="#f4f6f9")
        content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20),
        )

        table_frame = tk.Frame(
            content, bg="#ffffff", bd=1, relief="solid"
        )
        table_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10),
        )

        tk.Label(
            table_frame,
            text="Detailed Subject Breakdown",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
        ).pack(pady=10)

        # Line 68-73: The detailed Treeview. Notice we enforce zebra striping dynamically in load_data().
        cols = (
            "Sem",
            "Subject",
            "Total",
            "Cr",
            "GP",
            "Grade",
        )
        self.tree = ttk.Treeview(
            table_frame, columns=cols, show="headings"
        )
        for c in cols:
            self.tree.heading(c, text=c)
            w = 180 if c == "Subject" else 50
            self.tree.column(
                c, width=w, anchor="center"
            )
        self.tree.pack(
            fill="both", expand=True, padx=10, pady=10
        )

        # Line 76-83: We hook Matplotlib to a Tkinter Canvas to draw the SGPA line graph.
        graph_frame = tk.Frame(
            content,
            bg="#ffffff",
            bd=1,
            relief="solid",
            width=450,
        )
        graph_frame.pack(
            side="right", fill="both", expand=True
        )

        tk.Label(
            graph_frame,
            text="SGPA Progression",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
        ).pack(pady=10)

        self.fig, self.ax = plt.subplots(
            figsize=(5, 4), dpi=100
        )
        self.fig.patch.set_facecolor("#ffffff")
        self.canvas = FigureCanvasTkAgg(
            self.fig, master=graph_frame
        )
        self.canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=10
        )

        self.load_data()

    def load_data(self):
        # Line 88-93: We iterate the records, apply math (i % 2 == 0) for the 'evenrow' tag, and populate the tree.
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
                    g["grade_point"],
                    g["letter_grade"],
                ),
                tags=(tag,),
            )

        self.tree.tag_configure(
            "oddrow", background="#f2f2f2"
        )
        self.tree.tag_configure(
            "evenrow", background="#ffffff"
        )

        # Line 96-107: Clear the axis, plot the exact points, and set limits to a strict 10.5 to keep the chart visually stable.
        self.ax.clear()
        if self.sgpa_dict:
            sems = sorted(list(self.sgpa_dict.keys()))
            sgpas = [self.sgpa_dict[s] for s in sems]
            self.ax.plot(
                sems,
                sgpas,
                marker="o",
                linestyle="-",
                color="#e74c3c",
                linewidth=2,
                markersize=8,
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
                "No Data",
                ha="center",
                va="center",
                color="#7f8c8d",
            )
            self.ax.axis("off")
        self.canvas.draw()
