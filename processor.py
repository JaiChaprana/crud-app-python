import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self, db_conn):
        self.conn = db_conn

    def export_csv(self, path):
        pd.read_sql_query("SELECT * FROM students", self.conn).to_csv(path, index=False)

    def get_stats(self):
        """Calculates comprehensive stats using Pandas/Numpy."""
        df = pd.read_sql_query("SELECT age, semester FROM students", self.conn)

        if df.empty:
            return "Total Records: 0\nAvg Age: N/A\nMode Sem: N/A"

        # Calculations
        count = len(df)
        avg_age = np.mean(df['age'])

        # Get Mode of Semester
        mode_series = df['semester'].mode()
        mode_sem = mode_series[0] if not mode_series.empty else "N/A"

        return f"Total Records: {count}\nAvg Age: {avg_age:.1f}\nMode Sem: {mode_sem}"
