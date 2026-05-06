import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsWindow:
    def __init__(self, parent, engine):
        # Line 8-9: We ingest the Pandas engine singleton passed down from the AdminApp router.
        self.engine = engine

        self.window = tk.Toplevel(parent)
        self.window.title("Enterprise System Analytics Dashboard")
        self.window.geometry("1100x800")
        self.window.configure(bg="#f4f6f9")
        self.window.grab_set()

        self.setup_ui()

    def setup_ui(self):
        # --- HEADER & BOTTLENECK (Feature 6) ---
        header = tk.Frame(self.window, bg="#2c3e50", pady=15)
        header.pack(fill="x")

        tk.Label(
            header, text="University Data Insights",
            font=("Segoe UI", 16, "bold"), bg="#2c3e50", fg="white"
        ).pack()

        # Line 28: Execute the Pandas Bottleneck calculation from our engine.
        subj, mean_score = self.engine.get_bottleneck()

        # Line 31-35: Warn the admin immediately. We use a harsh red (#e74c3c) to flag the bottleneck.
        tk.Label(
            header,
            text=f"⚠️ CRITICAL BOTTLENECK COURSE: {subj} (Avg Score: {mean_score})",
            font=("Arial", 11, "bold"), fg="#e74c3c", bg="#2c3e50"
        ).pack(pady=(5, 0))

        # --- DYNAMIC PIVOT TABLE ENGINE (Feature 2) ---
        pivot_frame = tk.LabelFrame(self.window, text=" Pandas Dynamic Pivot Engine ", bg="#f4f6f9", font=("Arial", 11, "bold"), padx=15, pady=15)
        pivot_frame.pack(fill="x", padx=20, pady=20)

        ctrl_frame = tk.Frame(pivot_frame, bg="#f4f6f9")
        ctrl_frame.pack(fill="x", pady=(0, 10))

        tk.Label(ctrl_frame, text="Row Axis:", bg="#f4f6f9", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.row_cbo = ttk.Combobox(ctrl_frame, values=["program", "course", "batch"], state="readonly", width=15)
        self.row_cbo.set("program")
        self.row_cbo.pack(side="left", padx=5)

        tk.Label(ctrl_frame, text="Column Axis:", bg="#f4f6f9", font=("Arial", 10, "bold")).pack(side="left", padx=(20, 5))
        self.col_cbo = ttk.Combobox(ctrl_frame, values=["semester", "age"], state="readonly", width=15)
        self.col_cbo.set("semester")
        self.col_cbo.pack(side="left", padx=5)

        # Line 55: Bind the generation function to the button.
        ttk.Button(ctrl_frame, text="Generate Pivot Report", command=self.render_pivot).pack(side="left", padx=20)

        self.pivot_tree = ttk.Treeview(pivot_frame, show="headings", height=6)
        self.pivot_tree.pack(fill="both", expand=True)

        # Line 61: Auto-generate the default Program vs Semester pivot on load.
        self.render_pivot()

        # --- MATPLOTLIB VISUALIZATIONS (Legacy Support) ---
        graph_frame = tk.Frame(self.window, bg="#ffffff", bd=1, relief="solid")
        graph_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4), dpi=100)
        self.fig.patch.set_facecolor('#ffffff')

        self.draw_charts()

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def render_pivot(self):
        r_val = self.row_cbo.get()
        c_val = self.col_cbo.get()

        # Line 81: Request the aggregated DataFrame structures (Headers and Rows) from the Pandas engine.
        headers, rows = self.engine.generate_pivot(r_val, c_val, 'sap', 'count')

        # Line 84-85: Nuke the existing Treeview data and strictly redefine the physical columns.
        self.pivot_tree.delete(*self.pivot_tree.get_children())
        self.pivot_tree['columns'] = headers

        # Line 88-90: Dynamically rebuild the Tkinter headers based on the Pandas output.
        for h in headers:
            self.pivot_tree.heading(h, text=h)
            self.pivot_tree.column(h, anchor="center", width=100)

        # Line 93-96: Inject the dynamic rows and enforce your standard zebra striping mathematics.
        for i, row in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.pivot_tree.insert("", "end", values=row, tags=(tag,))

        self.pivot_tree.tag_configure('oddrow', background='#f2f2f2')
        self.pivot_tree.tag_configure('evenrow', background='#ffffff')

    def draw_charts(self):
        # Chart 1: Program Distribution (Unchanged logic, re-skinned)
        programs, counts = self.engine.get_program_distribution()
        if programs:
            self.ax1.pie(
                counts, labels=programs, autopct='%1.1f%%',
                startangle=140, colors=plt.cm.Paired.colors,
                wedgeprops=dict(width=0.4, edgecolor='w')
            )
            self.ax1.set_title("Students by Program", fontweight="bold")
        else:
            self.ax1.text(0.5, 0.5, "No Data", ha='center')

        # Chart 2: Semester Wise Student Count (Unchanged logic, re-skinned)
        semesters, counts = self.engine.get_semester_distribution()
        if semesters:
            sem_labels = [f"Sem {s}" for s in semesters]
            # Updated the bar color to match the #2c3e50 UI theme constraints.
            bars = self.ax2.bar(sem_labels, counts, color='#2c3e50')
            self.ax2.set_title("Student Count per Semester", fontweight="bold")
            self.ax2.set_ylabel("Number of Students")
            self.ax2.yaxis.get_major_locator().set_params(integer=True)

            for bar in bars:
                yval = bar.get_height()
                self.ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom')
        else:
            self.ax2.text(0.5, 0.5, "No Student Data", ha='center')
