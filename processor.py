import pandas as pd
import numpy as np
from datetime import datetime


class DataProcessor:
    def __init__(self, db_conn):

        self.conn = db_conn

    # ---------------------------------------------------------
    # LEGACY FEATURES: Imports, Exports, and Basic Distributions
    # ---------------------------------------------------------
    def export_csv(self, path):
        pd.read_sql_query(
            "SELECT * FROM students", self.conn
        ).to_csv(path, index=False)

    def get_program_distribution(self):
        df = pd.read_sql_query(
            "SELECT program, COUNT(sap) as count FROM students GROUP BY program",
            self.conn,
        )
        return (
            df["program"].tolist(),
            df["count"].tolist(),
        )

    def get_semester_distribution(self):
        # NOTE Group students by semester to feed the Matplotlib bar chart.
        df = pd.read_sql_query(
            "SELECT semester, COUNT(sap) as count FROM students GROUP BY semester ORDER BY semester",
            self.conn,
        )
        return (
            df["semester"].tolist(),
            df["count"].tolist(),
        )

    def import_csv(self, path, db, user):
        # NOTE ATTEMPTING TO READ THE CSV
        try:
            df = pd.read_csv(path)
            required_cols = {
                "sap",
                "name",
                "course",
                "program",
                "age",
                "semester",
                "email",
            }
            df.columns = (
                df.columns.str.strip().str.lower()
            )

            if not required_cols.issubset(
                set(df.columns)
            ):
                return (
                    False,
                    "CSV missing required columns.",
                )

            success_count = 0
            # NOTE - Iterate over rows, sanitize the data types, and apply the Smart Merge (add/update) logic.
            for _, row in df.iterrows():
                data = {
                    "sap": str(row.get("sap", ""))
                    .split(".")[0]
                    .strip(),
                    "name": str(
                        row.get("name", "")
                    ).strip(),
                    "course": str(
                        row.get("course", "")
                    ).strip(),
                    "program": str(
                        row.get("program", "")
                    ).strip(),
                    "age": str(row.get("age", ""))
                    .split(".")[0]
                    .strip(),
                    "semester": str(
                        row.get("semester", "")
                    )
                    .split(".")[0]
                    .strip(),
                    "email": str(
                        row.get("email", "")
                    ).strip(),
                }
                if len(data["sap"]) == 9:
                    existing = db.get_student(
                        data["sap"]
                    )
                    if existing:
                        db.update_student(
                            data["sap"], data
                        )
                    else:
                        db.add_student(data)
                    success_count += 1

            db.log_action(
                user,
                "BULK IMPORT",
                f"Imported {success_count} records.",
            )
            return (
                True,
                f"Imported {success_count} records.",
            )
        except Exception as e:
            return False, str(e)

    # ---------------------------------------------------------
    # FEATURE 1: Z-Score Anomaly Detector
    # ---------------------------------------------------------
    def get_anomalies(self):
        # NOTE Fetch all detailed grades into a DataFrame.
        df = pd.read_sql_query(
            "SELECT sap, semester, subject, mid_sem, end_sem, ct_1, ct_2, quiz_1, quiz_2 FROM grades_detailed",
            self.conn,
        )
        if df.empty:
            return []

        # NOTE Sum the components to get the total mark for each subject entry.
        df["total"] = df[
            [
                "mid_sem",
                "end_sem",
                "ct_1",
                "ct_2",
                "quiz_1",
                "quiz_2",
            ]
        ].sum(axis=1)

        # NOTE Calculate the mean (\mu) and standard deviation (\sigma) per cohort (semester + subject).
        df["mean"] = df.groupby(
            ["semester", "subject"]
        )["total"].transform("mean")
        df["std"] = df.groupby(
            ["semester", "subject"]
        )["total"].transform("std")

        # NOTE Calculate Z-Score mathematically. Handle division by zero.
        df["z_score"] = np.where(
            df["std"] > 0,
            (df["total"] - df["mean"]) / df["std"],
            0,
        )

        # NOTE  Filter out SAP IDs where the Z-score drops below -1.5 (statistically failing).
        anomalies = (
            df[df["z_score"] < -1.5]["sap"]
            .unique()
            .tolist()
        )
        return anomalies

    # ---------------------------------------------------------
    # FEATURE 2: Dynamic Pivot Table Engine
    # ---------------------------------------------------------
    def generate_pivot(
        self,
        index_col,
        columns_col,
        values_col,
        agg_func="count",
    ):
        # NOTE  Fetch core student data. Return empty lists if no data exists.
        df = pd.read_sql_query(
            "SELECT * FROM students", self.conn
        )
        if df.empty:
            return [], []

        # NOTE Use Pandas built-in pivot_table to cross-tabulate the user-selected axes.
        pivot = pd.pivot_table(
            df,
            values=values_col,
            index=index_col,
            columns=columns_col,
            aggfunc=agg_func,
            fill_value=0,
        )

        # NOTE Construct dynamic headers for Tkinter Treeview.
        headers = [index_col.title()] + [
            str(c) for c in pivot.columns
        ]

        # NOTE Unpack the DataFrame rows into standard Python lists so Tkinter can ingest them.
        rows = []
        for index, row in pivot.iterrows():
            rows.append([index] + row.tolist())
        return headers, rows

    # ---------------------------------------------------------
    # FEATURE 3: Forensic Audit Log Velocity Tracker
    # ---------------------------------------------------------
    def check_velocity_lockdown(self, logs_list):
        # NOTE: Iterate through recent logs (fetched by db layer) and count destructive "DELETE" actions.
        delete_count = sum(
            1
            for log in logs_list
            if "DELETE" in log[0].upper()
        )

        # NOTE If sum (DELETE) > 5 within the time delta t, return True to trigger UI lockdown.
        return delete_count > 5

    # ---------------------------------------------------------
    # FEATURE 4: Smart Defaults Data Entry
    # ---------------------------------------------------------
    def predict_defaults(self, program, semester):
        # NOTE  Fetch age and batch subsets based on the program and semester the user just typed.
        df = pd.read_sql_query(
            "SELECT age, batch FROM students WHERE program=? AND semester=?",
            self.conn,
            params=(program, semester),
        )
        if df.empty:
            return "", ""

        # NOTE  Calculate the statistical mode. If a mode exists, return it; otherwise return an empty string.
        pred_age = (
            int(df["age"].mode()[0])
            if not df["age"].mode().empty
            else ""
        )
        pred_batch = (
            str(df["batch"].mode()[0])
            if not df["batch"].mode().empty
            else ""
        )
        return pred_age, pred_batch

    # ---------------------------------------------------------
    # FEATURE 5: Predictive Grade Trajectory
    # ---------------------------------------------------------
    def predict_trajectory(self, sgpa_dict):
        # NOTE We need at least 2 data points (semesters) to draw a line.
        if len(sgpa_dict) < 2:
            return 0.0, "Insufficient Data"

        # NOTE Extract the dictionary into sorted X (semesters) and Y (sgpas) arrays for NumPy.
        sems = sorted(list(sgpa_dict.keys()))
        x = np.array(sems)
        y = np.array([sgpa_dict[s] for s in sems])

        # NOTE Apply Linear Regression (y = mx + c) using polyfit to find the slope (m) and intercept (c).
        slope, intercept = np.polyfit(x, y, 1)

        # NOTE Predict the SGPA for the upcoming semester and clamp the value between 0.0 and 10.0.
        next_sem = x[-1] + 1
        projected_sgpa = (slope * next_sem) + intercept
        projected_sgpa = min(
            max(projected_sgpa, 0.0), 10.0
        )

        # NOTE  Return the numerical prediction and the English string representation of the slope.
        trend = (
            "Upward"
            if slope > 0
            else ("Downward" if slope < 0 else "Flat")
        )
        return round(projected_sgpa, 2), trend

    # ---------------------------------------------------------
    # FEATURE 6: Curriculum Bottleneck Analyzer
    # ---------------------------------------------------------
    def get_bottleneck(self):
        # NOTE  Fetch all detailed grades and sum the components into a 'total' column.
        df = pd.read_sql_query(
            "SELECT subject, mid_sem, end_sem, ct_1, ct_2, quiz_1, quiz_2 FROM grades_detailed",
            self.conn,
        )
        if df.empty:
            return "No Data", 0.0
        df["total"] = df[
            [
                "mid_sem",
                "end_sem",
                "ct_1",
                "ct_2",
                "quiz_1",
                "quiz_2",
            ]
        ].sum(axis=1)

        # NOTE  Group by Subject and calculate the mean and count. Filter out subjects with <= 2 students.
        stats = (
            df.groupby("subject")["total"]
            .agg(["mean", "count"])
            .reset_index()
        )
        stats = stats[stats["count"] > 2]
        if stats.empty:
            return "Insufficient Data", 0.0

        # NOTE  Find the index of the minimum mean, extract that specific subject row, and return it.
        bottleneck = stats.loc[stats["mean"].idxmin()]
        return bottleneck["subject"], round(
            bottleneck["mean"], 2
        )
