# Student Management System (v5.6)
### *Enterprise-Grade Modular Desktop Registry & Analytics Suite*

A robust, strictly decoupled Student Information System (SIS) designed for high-performance academic administration. This version (v5.6) features a 7-layer modular architecture to handle curriculum mapping, forensic auditing, and integrated data visualization.

---

## 🏗 Modular Blueprint (The 7-File Architecture)

| Module | Classification | Responsibility |
| :--- | :--- | :--- |
| **main.py** | Orchestrator | Application entry point. Manages the `ttk` styling (Clam theme), sidebar navigation, and the primary Treeview registry. |
| **auth.py** | Security | The session gatekeeper. Handles login authentication and secures the entry point to the system. |
| **database.py** | Persistence | SQLite3 Data Access Layer. Manages schemas for `students`, `logs`, `curriculum`, and `grades`. |
| **processor.py** | Logic Engine | Data science layer powered by Pandas and NumPy. Handles CSV bulk I/O and GPA math. |
| **admin_dashboard.py** | Curriculum UI | Management interface for defining programs, subjects, and credit weightages. |
| **analytics_dashboard.py** | Visualization | Integrated Matplotlib dashboard rendering live student distribution charts. |
| **student_profile.py** | Deep-Dive UI | Individual record management including grade entry and live SGPA/CGPA calculation. |

---

## 🚀 Technical Core Logic

### 1. "Smart Merge" Update Algorithm
To maintain data integrity during edits, the system uses a non-destructive merge logic. If an input field in the UI is left empty during an update, the system automatically preserves the existing database value:

$$V_{final} = \begin{cases} \text{UI\_Input} & \text{if } \text{Input} \neq \emptyset \\ \text{DB\_Value} & \text{if } \text{Input} = \emptyset \end{cases}$$

### 2. Forensic Audit Trail
All data mutations (ADD, UPDATE, DELETE, BULK IMPORT) are recorded in the `logs` table. Every entry is timestamped and attributed to the specific user session captured during the `auth.py` sequence to ensure administrative accountability.

### 3. Integrated GPA Engine
Academic standing is calculated in real-time within `processor.py` using a weighted credit system:

$$\text{GPA} = \frac{\sum (\text{GradePoint} \times \text{Credits})}{\sum \text{Credits}}$$

**Grade Weights:** O: 10, A+: 9, A: 8, B+: 7, B: 6, C: 5, F: 0.

---

## 🛠 Setup & Installation

### Requirements
- Python 3.10+
- Pandas
- NumPy
- Matplotlib

### Execution Sequence
1. Install dependencies: `pip install pandas numpy matplotlib`
2. Launch the application: `python main.py`

---

## 🎨 UI/UX Standards
- **Theme Engine:** `ttk` 'clam'
- **Primary Palette:** Midnight Blue (#2c3e50), Sky Blue (#abd4ef), Emerald (#27ae60)
- **Data Display:** Zebra-striped Treeviews with 30px row height for optimal scannability.

---

## 🔐 System Access
- **Admin:** admin / 12345
- **Staff:** jai / 123
- **Staff:** a sai rao / 1234

---
*Note: This modular design allows the SQLite layer to be swapped for a cloud-based SQL instance without refactoring the GUI modules. Maintain this separation to avoid technical debt.*
