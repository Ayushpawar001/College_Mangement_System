import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
import hashlib
import os

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

from database import execute_query, fetch_all, get_connection


class CollegeManagementSystem:
    def __init__(self, root):
        self.root = root

        self.root.title("PRMCEAM")
        self.root.geometry("1440x900")
        self.root.minsize(1180, 760)

        # =====================================================
        # MODERN COLOR THEME
        # =====================================================

        self.bg = "#081431"
        self.white = "#F8FAFF"

        # Sidebar
        self.sidebar = "#07122E"
        self.sidebar_hover = "#182B61"
        self.sidebar_active = "#6D3DF5"

        # Main colors
        self.primary = "#7044F5"
        self.primary_dark = "#5430C9"
        self.secondary = "#E83E9F"
        self.cyan = "#1995FF"

        # Status colors
        self.success = "#10B981"
        self.danger = "#EF4444"
        self.warning = "#F59E0B"
        self.info = "#3B82F6"

        # Text
        self.text = "#F8FAFF"
        self.gray = "#A7B4D4"
        self.light_text = "#7786AC"

        # Borders
        self.border = "#203563"
        self.card_bg = "#101F43"

        # Module colors
        self.student_color = "#3B82F6"
        self.teacher_color = "#8B5CF6"
        self.course_color = "#06B6D4"
        self.attendance_color = "#10B981"
        self.marks_color = "#F59E0B"
        self.fees_color = "#EF4444"

        self.root.configure(bg=self.bg)

        self.setup_style()

        self.ensure_events_table()

        # =====================================================
        # MAIN CONTAINER
        # =====================================================

        self.main_container = tk.Frame(
            self.root,
            bg=self.bg
        )
        self.main_container.pack(
            fill="both",
            expand=True
        )

        # Sidebar
        self.create_sidebar()

        # Content area
        self.content = tk.Frame(
            self.main_container,
            bg=self.bg
        )
        self.content.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Header
        self.create_header()

        # Notebook
        self.notebook = ttk.Notebook(
            self.content
        )
        self.notebook.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18)
        )

        # Create all modules
        self.create_dashboard_tab()
        self.create_student_tab()
        self.create_teacher_tab()
        self.create_course_tab()
        self.create_attendance_tab()
        self.create_marks_tab()
        self.create_fees_tab()

        # Start with dashboard
        self.notebook.select(self.dashboard_tab)

        if self.nav_buttons:
            self.nav_buttons[0].configure(
                bg=self.sidebar_active,
                fg=self.white
            )

        self.update_dashboard()

    # =========================================================
    # STYLE
    # =========================================================

    def setup_style(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "TNotebook",
            background=self.bg,
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            padding=(18, 9),
            font=("Segoe UI", 10, "bold"),
            background="#14244A",
            foreground="#B4C0DD"
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", self.primary),
                ("active", "#243B72")
            ],
            foreground=[
                ("selected", self.white),
                ("active", self.white)
            ]
        )

        style.configure(
            "TFrame",
            background=self.bg
        )

        style.configure(
            "TLabel",
            background=self.bg,
            foreground=self.text,
            font=("Segoe UI", 10)
        )

        style.configure(
            "TLabelframe",
            background=self.card_bg,
            bordercolor=self.border,
            relief="solid"
        )

        style.configure(
            "TLabelframe.Label",
            background=self.card_bg,
            foreground="#BBA8FF",
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "TEntry",
            padding=8,
            font=("Segoe UI", 10)
        )

        style.configure(
            "TCombobox",
            padding=7,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview",
            background="#102044",
            fieldbackground="#102044",
            foreground="#DDE5FF",
            rowheight=34,
            font=("Segoe UI", 9),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#1A2E5D",
            foreground=self.white,
            font=("Segoe UI", 10, "bold"),
            padding=10
        )

        style.map(
            "Treeview",
            background=[
                ("selected", "#3A4F88")
            ],
            foreground=[
                ("selected", self.white)
            ]
        )

    # =========================================================
    # SIDEBAR
    # =========================================================

    def create_sidebar(self):
        self.sidebar_frame = tk.Frame(
            self.main_container,
            bg=self.sidebar,
            width=220
        )
        self.sidebar_frame.pack(
            side="left",
            fill="y"
        )
        self.sidebar_frame.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(
            self.sidebar_frame,
            bg=self.sidebar
        )
        logo_frame.pack(
            fill="x",
            pady=(24, 26)
        )

        tk.Label(
            logo_frame,
            text="PRMCEAM",
            bg=self.sidebar,
            fg="#E83E9F",
            font=("Segoe UI", 22, "bold")
        ).pack()

        tk.Label(
            logo_frame,
            text="PRMCEAM",
            bg=self.sidebar,
            fg=self.white,
            font=("Segoe UI", 17, "bold")
        ).pack()

        tk.Label(
            logo_frame,
            text="COLLEGE MANAGEMENT SYSTEM",
            bg=self.sidebar,
            fg="#8FA4D5",
            font=("Segoe UI", 8, "bold")
        ).pack(pady=(3, 0))

        tk.Label(
            self.sidebar_frame,
            text="MAIN MENU",
            bg=self.sidebar,
            fg="#647BA8",
            font=("Segoe UI", 8, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 10)
        )

        self.nav_buttons = []

        navigation = [
            ("⌂   Dashboard", 0),
            ("♙   Students", 1),
            ("♙   Teachers", 2),
            ("▣   Courses", 3),
            ("✓   Attendance", 4),
            ("▥   Marks", 5),
            ("$   Fees", 6)
        ]

        for name, index in navigation:
            btn = tk.Button(
                self.sidebar_frame,
                text=name,
                anchor="w",
                bg=self.sidebar,
                fg="#B8C5E5",
                activebackground=self.sidebar_hover,
                activeforeground=self.white,
                relief="flat",
                bd=0,
                font=("Segoe UI", 10, "bold"),
                padx=18,
                pady=10,
                cursor="hand2",
                command=lambda i=index: self.open_tab(i)
            )

            btn.pack(
                fill="x",
                padx=12,
                pady=3
            )

            def enter(event, b=btn):
                if b != self.nav_buttons[self.get_current_tab_index()]:
                    b.configure(
                        bg=self.sidebar_hover,
                        fg=self.white
                    )

            def leave(event, b=btn):
                current = self.get_current_tab_index()
                if current < len(self.nav_buttons) and b == self.nav_buttons[current]:
                    b.configure(
                        bg=self.sidebar_active,
                        fg=self.white
                    )
                else:
                    b.configure(
                        bg=self.sidebar,
                        fg="#B8C5E5"
                    )

            btn.bind("<Enter>", enter)
            btn.bind("<Leave>", leave)

            self.nav_buttons.append(btn)

        # Bottom status
        bottom = tk.Frame(
            self.sidebar_frame,
            bg="#1E293B"
        )
        bottom.pack(
            side="bottom",
            fill="x",
            padx=12,
            pady=15
        )

        tk.Label(
            bottom,
            text="●",
            bg="#1E293B",
            fg="#10B981",
            font=("Segoe UI", 18)
        ).pack(
            side="left",
            padx=(10, 5),
            pady=8
        )

        tk.Label(
            bottom,
            text="System Online",
            bg="#1E293B",
            fg="#E2E8F0",
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

    def get_current_tab_index(self):
        try:
            return self.notebook.index(self.notebook.select())
        except Exception:
            return 0

    # =========================================================
    # HEADER
    # =========================================================

    def create_header(self):
        header = tk.Frame(
            self.content,
            bg=self.bg,
            height=78
        )
        header.pack(
            fill="x",
            padx=20,
            pady=(12, 4)
        )
        header.pack_propagate(False)

        left = tk.Frame(
            header,
            bg=self.bg
        )
        left.pack(
            side="left",
            fill="y"
        )

        self.page_title = tk.Label(
            left,
            text="Welcome back, Ayush Pawar!",
            bg=self.bg,
            fg=self.white,
            font=("Segoe UI", 20, "bold")
        )
        self.page_title.pack(
            anchor="w",
            pady=(8, 0)
        )

        tk.Label(
            left,
            text="Here's what's happening in your college today.",
            bg=self.bg,
            fg=self.gray,
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        right = tk.Frame(
            header,
            bg=self.bg
        )
        right.pack(
            side="right",
            fill="y"
        )

        self.search_entry = tk.Entry(
            right,
            width=27,
            bg="#111F42",
            fg="#DCE5FF",
            insertbackground=self.white,
            relief="flat",
            bd=0,
            font=("Segoe UI", 9)
        )
        self.search_entry.insert(0, "Search anything...")
        self.search_entry.configure(fg="#7786AC")
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_search_placeholder)
        self.search_entry.bind("<Return>", self.search_records)
        self.search_entry.pack(side="left", padx=(0, 18), ipady=9)

        tk.Label(
            right,
            text=date.today().strftime("%d %b %Y"),
            bg=self.bg,
            fg="#B9C5E2",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", pady=(8, 0))

    def clear_search_placeholder(self, event=None):
        if self.search_entry.get() == "Search anything...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(fg="#DCE5FF")

    def restore_search_placeholder(self, event=None):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search anything...")
            self.search_entry.configure(fg="#7786AC")

    def search_records(self, event=None):
        term = self.search_entry.get().strip()
        if not term or term == "Search anything...":
            return

        matches = []
        term = term.casefold()
        entities = (
            ("Students", "students", ("student_id", "name", "course", "phone", "email")),
            ("Teachers", "teachers", ("teacher_id", "name", "subject", "phone", "email")),
            ("Courses", "courses", ("course_id", "course_name", "duration", "fees")),
            ("Attendance", "attendance", ("attendance_id", "student_id", "attendance_date", "status")),
            ("Marks", "marks", ("mark_id", "student_id", "subject", "marks")),
            ("Fees", "fees", ("fee_id", "student_id", "amount", "payment_date", "status")),
        )

        for label, table, columns in entities:
            rows = fetch_all(f"SELECT {', '.join(columns)} FROM {table}")
            for row in rows:
                if term in " ".join(str(value) for value in row).casefold():
                    matches.append((label, row))

        results = tk.Toplevel(self.root)
        results.title(f"Search results for '{self.search_entry.get().strip()}'")
        results.geometry("760x420")
        results.configure(bg=self.bg)

        tk.Label(
            results,
            text=f"{len(matches)} result(s) found",
            bg=self.bg,
            fg=self.white,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 8))

        tree = ttk.Treeview(results, columns=("module", "record"), show="headings")
        tree.heading("module", text="Module")
        tree.heading("record", text="Record")
        tree.column("module", width=130, anchor="w")
        tree.column("record", width=580, anchor="w")
        tree.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        for label, row in matches:
            tree.insert("", tk.END, values=(label, " | ".join(str(value) for value in row)))

    # =========================================================
    # TAB NAVIGATION
    # =========================================================

    def open_tab(self, index):
        self.notebook.select(index)

        names = [
            "Dashboard",
            "Students",
            "Teachers",
            "Courses",
            "Attendance",
            "Marks",
            "Fees"
        ]

        self.page_title.config(
            text=names[index]
        )

        for btn in self.nav_buttons:
            btn.configure(
                bg=self.sidebar,
                fg="#CBD5E1"
            )

        if index < len(self.nav_buttons):
            self.nav_buttons[index].configure(
                bg=self.sidebar_active,
                fg=self.white
            )

        if index == 0:
            self.update_dashboard()

        elif index == 1:
            self.load_students()

        elif index == 2:
            self.load_teachers()

        elif index == 3:
            self.load_courses()

        elif index == 4:
            self.load_attendance()

        elif index == 5:
            self.load_marks()

        elif index == 6:
            self.load_fees()

    # =========================================================
    # COMMON FUNCTIONS
    # =========================================================

    def clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def create_button(self, parent, text, command, bg=None):
        if bg is None:
            bg = self.primary

        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=self.white,
            activebackground=self.primary_dark,
            activeforeground=self.white,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=9,
            cursor="hand2"
        )

        def on_enter(event):
            btn.configure(bg=self.primary_dark)

        def on_leave(event):
            btn.configure(bg=bg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def student_exists(self, student_id):
        rows = fetch_all(
            """
            SELECT student_id
            FROM students
            WHERE student_id=%s
            """,
            (student_id,)
        )
        return len(rows) > 0

    def validate_date(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # =========================================================
    # DASHBOARD
    # =========================================================

    def create_dashboard_tab(self):
        self.dashboard_tab = ttk.Frame(self.notebook)

        self.notebook.add(
            self.dashboard_tab,
            text="Dashboard"
        )

        # Welcome banner
        welcome = tk.Frame(
            self.dashboard_tab,
            bg="#EEF2FF",
            highlightbackground="#C7D2FE",
            highlightthickness=1
        )
        welcome.pack(
            fill="x",
            padx=15,
            pady=15
        )

        tk.Frame(
            welcome,
            bg="#4F46E5",
            width=7
        ).pack(
            side="left",
            fill="y"
        )

        tk.Label(
            welcome,
            text="Welcome to PRMCEAM",
            bg="#EEF2FF",
            fg="#312E81",
            font=("Segoe UI", 19, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(18, 3)
        )

        tk.Label(
            welcome,
            text="Manage students, teachers, courses, attendance, marks and fees from one place.",
            bg="#EEF2FF",
            fg="#64748B",
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 18)
        )

        # Statistics cards
        cards = tk.Frame(
            self.dashboard_tab,
            bg=self.bg
        )
        cards.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.dashboard_cards = {}

        card_info = [
            ("Students", "0", self.student_color, "S"),
            ("Teachers", "0", self.teacher_color, "T"),
            ("Courses", "0", self.course_color, "C"),
            ("Attendance", "0", self.attendance_color, "A"),
            ("Marks", "0", self.marks_color, "M"),
            ("Fee Records", "0", self.fees_color, "F")
        ]

        for i, (title, value, color, icon) in enumerate(card_info):
            card = tk.Frame(
                cards,
                bg=self.white,
                highlightbackground=self.border,
                highlightthickness=1
            )

            card.grid(
                row=0,
                column=i,
                padx=6,
                pady=8,
                sticky="nsew"
            )

            cards.columnconfigure(
                i,
                weight=1
            )

            tk.Frame(
                card,
                bg=color,
                height=5
            ).pack(fill="x")

            icon_circle = tk.Frame(
                card,
                bg=color,
                width=38,
                height=38
            )
            icon_circle.pack(
                anchor="w",
                padx=15,
                pady=(12, 5)
            )
            icon_circle.pack_propagate(False)

            tk.Label(
                icon_circle,
                text=icon,
                bg=color,
                fg=self.white,
                font=("Segoe UI", 12, "bold")
            ).pack(
                expand=True
            )

            tk.Label(
                card,
                text=title,
                bg=self.white,
                fg=self.gray,
                font=("Segoe UI", 9, "bold")
            ).pack(
                anchor="w",
                padx=15
            )

            value_label = tk.Label(
                card,
                text=value,
                bg=self.white,
                fg=color,
                font=("Segoe UI", 24, "bold")
            )
            value_label.pack(
                anchor="w",
                padx=15,
                pady=(0, 15)
            )

            self.dashboard_cards[title] = value_label

        # Quick actions
        quick = ttk.LabelFrame(
            self.dashboard_tab,
            text="Quick Actions",
            padding=20
        )
        quick.pack(
            fill="x",
            padx=15,
            pady=20
        )

        self.create_button(
            quick,
            "Add Student",
            lambda: self.open_tab(1),
            self.student_color
        ).pack(side="left", padx=7)

        self.create_button(
            quick,
            "Take Attendance",
            lambda: self.open_tab(4),
            self.attendance_color
        ).pack(side="left", padx=7)

        self.create_button(
            quick,
            "Enter Marks",
            lambda: self.open_tab(5),
            self.marks_color
        ).pack(side="left", padx=7)

        self.create_button(
            quick,
            "Record Fees",
            lambda: self.open_tab(6),
            self.fees_color
        ).pack(side="left", padx=7)

        # System status
        info = tk.Frame(
            self.dashboard_tab,
            bg="#ECFDF5",
            highlightbackground="#A7F3D0",
            highlightthickness=1
        )
        info.pack(
            fill="x",
            padx=15,
            pady=5
        )

        tk.Label(
            info,
            text="SYSTEM STATUS",
            bg="#ECFDF5",
            fg="#059669",
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 3)
        )

        tk.Label(
            info,
            text="All modules are connected to your MySQL database.",
            bg="#ECFDF5",
            fg=self.text,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

    def update_dashboard(self):
        try:
            students = fetch_all("SELECT student_id FROM students")
            teachers = fetch_all("SELECT teacher_id FROM teachers")
            courses = fetch_all("SELECT course_id FROM courses")
            attendance = fetch_all("SELECT attendance_id FROM attendance")
            marks = fetch_all("SELECT mark_id FROM marks")
            fees = fetch_all("SELECT fee_id FROM fees")
            fee_total = fetch_all(
                "SELECT COALESCE(SUM(amount), 0) FROM fees"
            )
            daily_presence = fetch_all(
                """
                SELECT attendance_date,
                       ROUND(
                           100 * SUM(CASE WHEN LOWER(status) = 'present' THEN 1 ELSE 0 END)
                           / NULLIF(COUNT(*), 0),
                           0
                       )
                FROM attendance
                WHERE attendance_date >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
                GROUP BY attendance_date
                ORDER BY attendance_date
                """
            )
            today_attendance = fetch_all(
                """
                SELECT status, COUNT(*)
                FROM attendance
                WHERE attendance_date=%s
                GROUP BY status
                """,
                (date.today(),)
            )

            total_amount = fee_total[0][0] if fee_total else 0
            if total_amount is None:
                total_amount = 0

            values = {
                "Students": len(students),
                "Teachers": len(teachers),
                "Courses": len(courses),
                "Attendance": len(attendance),
                "Marks": len(marks),
                "Fee Records": f"Rs {float(total_amount):,.0f}"
            }

            for key, value in values.items():
                self.dashboard_cards[key].config(
                    text=str(value)
                )

            present = sum(count for status, count in today_attendance if str(status).lower() == "present")
            absent = sum(count for status, count in today_attendance if str(status).lower() == "absent")
            self.draw_attendance_chart(daily_presence)
            self.update_attendance_summary(present, absent)
            self.load_recent_students()
            self.load_events()

        except Exception:
            pass

    # =========================================================
    # STUDENT MODULE
    # =========================================================

    def create_student_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Students")

        form = ttk.LabelFrame(
            tab,
            text="Student Information",
            padding=15
        )
        form.pack(
            fill="x",
            padx=15,
            pady=15
        )

        labels = [
            "Name", "Age", "Gender", "Course",
            "Year", "Phone", "Email", "Address"
        ]

        self.student_entries = {}

        for i, label in enumerate(labels):
            row = (i // 4) * 2
            col = i % 4

            ttk.Label(
                form,
                text=label
            ).grid(
                row=row,
                column=col,
                sticky="w",
                padx=8,
                pady=(2, 4)
            )

            entry = ttk.Entry(
                form,
                width=25
            )
            entry.grid(
                row=row + 1,
                column=col,
                padx=8,
                pady=(0, 8)
            )

            self.student_entries[label] = entry

        buttons = tk.Frame(
            tab,
            bg=self.bg
        )
        buttons.pack(
            fill="x",
            padx=15,
            pady=(0, 8)
        )

        self.create_button(
            buttons, "Add Student",
            self.add_student,
            self.student_color
        ).pack(side="left", padx=4)

        self.create_button(
            buttons, "Update",
            self.update_student,
            self.primary
        ).pack(side="left", padx=4)

        self.create_button(
            buttons, "Delete",
            self.delete_student,
            self.danger
        ).pack(side="left", padx=4)

        self.create_button(
            buttons, "Clear",
            self.clear_student_form,
            self.gray
        ).pack(side="left", padx=4)

        self.create_button(
            buttons, "Refresh",
            self.load_students,
            self.success
        ).pack(side="left", padx=4)

        table_frame = tk.Frame(
            tab,
            bg=self.white
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )

        columns = (
            "ID", "Name", "Age", "Gender", "Course",
            "Year", "Phone", "Email", "Address"
        )

        self.student_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        widths = [
            60, 160, 60, 90, 130,
            70, 120, 190, 220
        ]

        for column, width in zip(columns, widths):
            self.student_tree.heading(
                column,
                text=column
            )
            self.student_tree.column(
                column,
                width=width
            )

        scroll_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.student_tree.yview
        )

        scroll_x = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.student_tree.xview
        )

        self.student_tree.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        self.student_tree.pack(
            side="top",
            fill="both",
            expand=True
        )

        scroll_y.pack(
            side="right",
            fill="y"
        )

        scroll_x.pack(
            side="bottom",
            fill="x"
        )

        self.student_tree.bind(
            "<<TreeviewSelect>>",
            self.select_student
        )

        self.load_students()

    def add_student(self):
        e = self.student_entries

        if not e["Name"].get().strip():
            messagebox.showwarning(
                "Missing Information",
                "Please enter student name."
            )
            return

        if not e["Course"].get().strip():
            messagebox.showwarning(
                "Missing Information",
                "Please enter course."
            )
            return

        try:
            age = int(e["Age"].get())
            year = int(e["Year"].get())

            if age <= 0 or year <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Age and Year must be valid positive numbers."
            )
            return

        query = """
        INSERT INTO students
        (name, age, gender, course, year, phone, email, address)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            e["Name"].get().strip(),
            age,
            e["Gender"].get().strip(),
            e["Course"].get().strip(),
            year,
            e["Phone"].get().strip(),
            e["Email"].get().strip(),
            e["Address"].get().strip()
        )

        try:
            if execute_query(query, values):
                messagebox.showinfo(
                    "Success",
                    "Student added successfully."
                )
                self.clear_student_form()
                self.load_students()
                self.update_dashboard()

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )

    def update_student(self):
        selected = self.student_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Student",
                "Please select a student from the table."
            )
            return

        student_id = selected[0]

        e = self.student_entries

        try:
            age = int(e["Age"].get())
            year = int(e["Year"].get())

            if age <= 0 or year <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Age and Year must be valid positive numbers."
            )
            return

        query = """
        UPDATE students
        SET name=%s,
            age=%s,
            gender=%s,
            course=%s,
            year=%s,
            phone=%s,
            email=%s,
            address=%s
        WHERE student_id=%s
        """

        values = (
            e["Name"].get().strip(),
            age,
            e["Gender"].get().strip(),
            e["Course"].get().strip(),
            year,
            e["Phone"].get().strip(),
            e["Email"].get().strip(),
            e["Address"].get().strip(),
            student_id
        )

        try:
            if execute_query(query, values):
                messagebox.showinfo(
                    "Success",
                    "Student updated successfully."
                )
                self.clear_student_form()
                self.load_students()
                self.update_dashboard()

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )

    def delete_student(self):
        selected = self.student_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Student",
                "Please select a student."
            )
            return

        # The Treeview item ID is the database ID; the first displayed value is only a serial number.
        student_id = selected[0]

        if messagebox.askyesno(
            "Confirm Delete",
            "Delete this student?\n\nRelated attendance, marks or fees may also be affected."
        ):
            try:
                if execute_query(
                    "DELETE FROM students WHERE student_id=%s",
                    (student_id,)
                ):
                    messagebox.showinfo(
                        "Success",
                        "Student deleted successfully."
                    )
                    self.clear_student_form()
                    self.load_students()
                    self.update_dashboard()

            except Exception as error:
                messagebox.showerror(
                    "Delete Failed",
                    str(error)
                )

    def clear_student_form(self):
        for entry in self.student_entries.values():
            entry.delete(0, tk.END)

    def select_student(self, event=None):
        selected = self.student_tree.selection()

        if not selected:
            return

        values = self.student_tree.item(
            selected[0]
        )["values"]

        entries = list(
            self.student_entries.values()
        )

        for entry, value in zip(
            entries,
            values[1:]
        ):
            entry.delete(0, tk.END)
            entry.insert(0, value)

    def load_students(self):
        rows = fetch_all(
            """
            SELECT student_id,name,age,gender,
                   course,year,phone,email,address
            FROM students
            ORDER BY student_id DESC
            """
        )

        self.clear_tree(self.student_tree)

        for display_id, row in enumerate(rows, start=1):
            self.student_tree.insert(
                "",
                tk.END,
                iid=str(row[0]),
                values=(display_id, *row[1:])
            )

        self.refresh_attendance_students()
        self.refresh_marks_students()
        self.refresh_fee_students()

    def refresh_attendance_students(self):
        if not hasattr(self, "attendance_student_id"):
            return

        student_rows = fetch_all(
            "SELECT student_id, name FROM students ORDER BY student_id"
        )
        self.attendance_student_map = {
            name: student_id
            for student_id, name in student_rows
        }
        student_options = [name for _, name in student_rows]
        self.attendance_student_id["values"] = student_options

        if student_options:
            if self.attendance_student_id.get() not in student_options:
                self.attendance_student_id.current(0)
        else:
            self.attendance_student_id.set("")

    def refresh_marks_students(self):
        if not hasattr(self, "marks_student_id"):
            return
        student_rows = fetch_all("SELECT student_id, name FROM students ORDER BY student_id")
        self.marks_student_map = {name: student_id for student_id, name in student_rows}
        options = [name for _, name in student_rows]
        self.marks_student_id["values"] = options
        if options:
            self.marks_student_id.current(0)
        else:
            self.marks_student_id.set("")

    def refresh_fee_students(self):
        if not hasattr(self, "fee_student_id"):
            return
        student_rows = fetch_all("SELECT student_id, name FROM students ORDER BY student_id")
        self.fee_student_map = {name: student_id for student_id, name in student_rows}
        options = [name for _, name in student_rows]
        self.fee_student_id["values"] = options
        if options:
            self.fee_student_id.current(0)
        else:
            self.fee_student_id.set("")

    # =========================================================
    # TEACHER MODULE
    # =========================================================

    def create_teacher_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Teachers")

        form = ttk.LabelFrame(
            tab,
            text="Teacher Information",
            padding=15
        )
        form.pack(
            fill="x",
            padx=15,
            pady=15
        )

        labels = [
            "Name",
            "Subject",
            "Phone",
            "Email"
        ]

        self.teacher_entries = {}

        for i, label in enumerate(labels):
            ttk.Label(
                form,
                text=label
            ).grid(
                row=0,
                column=i,
                sticky="w",
                padx=10
            )

            entry = ttk.Entry(
                form,
                width=28
            )
            entry.grid(
                row=1,
                column=i,
                padx=10,
                pady=8
            )

            self.teacher_entries[label] = entry

        buttons = tk.Frame(
            tab,
            bg=self.bg
        )
        buttons.pack(
            fill="x",
            padx=15
        )

        self.create_button(
            buttons,
            "Add Teacher",
            self.add_teacher,
            self.teacher_color
        ).pack(side="left", padx=4)

        self.create_button(
            buttons,
            "Delete",
            self.delete_teacher,
            self.danger
        ).pack(side="left", padx=4)

        self.create_button(
            buttons,
            "Clear",
            self.clear_teacher,
            self.gray
        ).pack(side="left", padx=4)

        self.create_button(
            buttons,
            "Refresh",
            self.load_teachers,
            self.success
        ).pack(side="left", padx=4)

        columns = (
            "ID",
            "Name",
            "Subject",
            "Phone",
            "Email"
        )

        self.teacher_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings"
        )

        for column in columns:
            self.teacher_tree.heading(
                column,
                text=column
            )
            self.teacher_tree.column(
                column,
                width=200
            )

        self.teacher_tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.load_teachers()

    def add_teacher(self):
        e = self.teacher_entries

        if not e["Name"].get().strip():
            messagebox.showwarning(
                "Warning",
                "Please enter teacher name."
            )
            return

        query = """
        INSERT INTO teachers
        (name,subject,phone,email)
        VALUES (%s,%s,%s,%s)
        """

        values = (
            e["Name"].get().strip(),
            e["Subject"].get().strip(),
            e["Phone"].get().strip(),
            e["Email"].get().strip()
        )

        try:
            if execute_query(query, values):
                messagebox.showinfo(
                    "Success",
                    "Teacher added successfully."
                )
                self.clear_teacher()
                self.load_teachers()
                self.update_dashboard()

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )

    def delete_teacher(self):
        selected = self.teacher_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a teacher."
            )
            return

        teacher_id = selected[0]

        if messagebox.askyesno(
            "Confirm",
            "Delete selected teacher?"
        ):
            try:
                if execute_query(
                    "DELETE FROM teachers WHERE teacher_id=%s",
                    (teacher_id,)
                ):
                    messagebox.showinfo(
                        "Success",
                        "Teacher deleted successfully."
                    )

                self.load_teachers()
                self.update_dashboard()

            except Exception as error:
                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

    def clear_teacher(self):
        for entry in self.teacher_entries.values():
            entry.delete(0, tk.END)

    def load_teachers(self):
        rows = fetch_all(
            """
            SELECT teacher_id,name,subject,phone,email
            FROM teachers
            ORDER BY teacher_id DESC
            """
        )

        self.clear_tree(self.teacher_tree)

        for display_id, row in enumerate(rows, start=1):
            self.teacher_tree.insert(
                "",
                tk.END,
                iid=str(row[0]),
                values=(display_id, *row[1:])
            )

    # =========================================================
    # COURSE MODULE
    # =========================================================

    def create_course_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Courses")

        form = ttk.LabelFrame(
            tab,
            text="Course Information",
            padding=15
        )
        form.pack(
            fill="x",
            padx=15,
            pady=15
        )

        ttk.Label(
            form,
            text="Course Name"
        ).grid(row=0, column=0)

        self.course_name = ttk.Entry(
            form,
            width=30
        )
        self.course_name.grid(
            row=1,
            column=0,
            padx=10,
            pady=8
        )

        ttk.Label(
            form,
            text="Duration (Years)"
        ).grid(row=0, column=1)

        self.course_duration = ttk.Entry(
            form,
            width=20
        )
        self.course_duration.grid(
            row=1,
            column=1,
            padx=10
        )

        ttk.Label(
            form,
            text="Fees"
        ).grid(row=0, column=2)

        self.course_fees = ttk.Entry(
            form,
            width=20
        )
        self.course_fees.grid(
            row=1,
            column=2,
            padx=10
        )

        self.create_button(
            form,
            "Add Course",
            self.add_course,
            self.course_color
        ).grid(
            row=1,
            column=3,
            padx=10
        )

        self.create_button(
            form,
            "Delete",
            self.delete_course,
            self.danger
        ).grid(
            row=1,
            column=4,
            padx=10
        )

        columns = (
            "ID",
            "Course Name",
            "Duration",
            "Fees"
        )

        self.course_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings"
        )

        for column in columns:
            self.course_tree.heading(
                column,
                text=column
            )
            self.course_tree.column(
                column,
                width=250
            )

        self.course_tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.load_courses()

    def add_course(self):
        if not self.course_name.get().strip():
            messagebox.showwarning(
                "Warning",
                "Please enter course name."
            )
            return

        try:
            duration = int(
                self.course_duration.get()
            )

            fees = float(
                self.course_fees.get()
            )

            if duration <= 0 or fees < 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Duration must be positive and fees must be a valid number."
            )
            return

        query = """
        INSERT INTO courses
        (course_name,duration,fees)
        VALUES (%s,%s,%s)
        """

        try:
            if execute_query(
                query,
                (
                    self.course_name.get().strip(),
                    duration,
                    fees
                )
            ):
                messagebox.showinfo(
                    "Success",
                    "Course added successfully."
                )

                self.course_name.delete(0, tk.END)
                self.course_duration.delete(0, tk.END)
                self.course_fees.delete(0, tk.END)

                self.load_courses()
                self.update_dashboard()

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )

    def delete_course(self):
        selected = self.course_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a course."
            )
            return

        course_id = selected[0]

        if messagebox.askyesno(
            "Confirm",
            "Delete selected course?"
        ):
            try:
                if execute_query(
                    "DELETE FROM courses WHERE course_id=%s",
                    (course_id,)
                ):
                    messagebox.showinfo(
                        "Success",
                        "Course deleted successfully."
                    )

                self.load_courses()
                self.update_dashboard()

            except Exception as error:
                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

    def load_courses(self):
        rows = fetch_all(
            """
            SELECT course_id,course_name,duration,fees
            FROM courses
            ORDER BY course_id DESC
            """
        )

        self.clear_tree(self.course_tree)

        for display_id, row in enumerate(rows, start=1):
            self.course_tree.insert(
                "",
                tk.END,
                iid=str(row[0]),
                values=(display_id, *row[1:])
            )

    # =========================================================
    # ATTENDANCE MODULE
    # =========================================================

    def create_attendance_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Attendance")

        header = tk.Frame(
            tab,
            bg="#ECFDF5",
            highlightbackground="#A7F3D0",
            highlightthickness=1
        )
        header.pack(
            fill="x",
            padx=15,
            pady=(15, 5)
        )

        tk.Label(
            header,
            text="Attendance Management",
            bg="#ECFDF5",
            fg="#059669",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(12, 2)
        )

        tk.Label(
            header,
            text="Record daily attendance for students",
            bg="#ECFDF5",
            fg=self.gray,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 12)
        )

        form = ttk.LabelFrame(
            tab,
            text="Record Attendance",
            padding=15
        )
        form.pack(
            fill="x",
            padx=15,
            pady=10
        )

        ttk.Label(
            form,
            text="Student ID"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.attendance_student_id = ttk.Combobox(
            form,
            width=18,
            state="readonly"
        )
        self.attendance_student_id.grid(
            row=1,
            column=0,
            padx=(0, 15),
            pady=6
        )
        self.refresh_attendance_students()

        ttk.Label(
            form,
            text="Date (YYYY-MM-DD)"
        ).grid(
            row=0,
            column=1,
            sticky="w"
        )

        self.attendance_date = ttk.Entry(
            form,
            width=20
        )
        self.attendance_date.insert(
            0,
            str(date.today())
        )
        self.attendance_date.grid(
            row=1,
            column=1,
            padx=15
        )

        ttk.Label(
            form,
            text="Status"
        ).grid(
            row=0,
            column=2,
            sticky="w"
        )

        self.attendance_status = ttk.Combobox(
            form,
            values=["Present", "Absent"],
            state="readonly",
            width=18
        )
        self.attendance_status.set("Present")
        self.attendance_status.grid(
            row=1,
            column=2,
            padx=15
        )

        self.create_button(
            form,
            "Save Attendance",
            self.add_attendance,
            self.attendance_color
        ).grid(
            row=1,
            column=3,
            padx=10
        )

        self.create_button(
            form,
            "Clear",
            self.clear_attendance,
            self.gray
        ).grid(
            row=1,
            column=4,
            padx=5
        )

        self.create_button(
            form,
            "Delete Selected",
            self.delete_attendance,
            self.danger
        ).grid(
            row=1,
            column=5,
            padx=5
        )

        tk.Label(
            tab,
            text="Attendance History",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 3)
        )

        self.attendance_tree = ttk.Treeview(
            tab,
            columns=("ID", "Student", "Date", "Status"),
            show="headings"
        )

        widths = [100, 160, 220, 180]

        for column, width in zip(
            self.attendance_tree["columns"],
            widths
        ):
            self.attendance_tree.heading(
                column,
                text=column
            )
            self.attendance_tree.column(
                column,
                width=width
            )

        self.attendance_tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.load_attendance()

    def add_attendance(self):
        student_text = (
            self.attendance_student_id
            .get()
            .strip()
        )

        if not student_text:
            messagebox.showwarning(
                "Missing Student ID",
                "Please enter Student ID."
            )
            return

        student_id = self.attendance_student_map.get(student_text)
        if student_id is None:
            messagebox.showerror(
                "Invalid Student ID",
                "Please select a student from the list."
            )
            return

        if not self.student_exists(student_id):
            messagebox.showerror(
                "Student Not Found",
                f"Student ID {student_id} does not exist."
            )
            return

        attendance_date = (
            self.attendance_date
            .get()
            .strip()
        )

        if not self.validate_date(attendance_date):
            messagebox.showerror(
                "Invalid Date",
                "Please enter date in YYYY-MM-DD format."
            )
            return

        status = self.attendance_status.get()

        query = """
        INSERT INTO attendance
        (student_id,attendance_date,status)
        VALUES (%s,%s,%s)
        """

        try:
            if execute_query(
                query,
                (
                    student_id,
                    attendance_date,
                    status
                )
            ):
                messagebox.showinfo(
                    "Success",
                    "Attendance saved successfully."
                )

                self.clear_attendance()
                self.load_attendance()
                self.update_dashboard()

        except Exception as error:
            messagebox.showerror(
                "Attendance Error",
                str(error)
            )

    def clear_attendance(self):
        self.attendance_student_id.delete(
            0,
            tk.END
        )

        self.attendance_date.delete(
            0,
            tk.END
        )

        self.attendance_date.insert(
            0,
            str(date.today())
        )

        self.attendance_status.set("Present")

    def delete_attendance(self):
        selected = self.attendance_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Record",
                "Please select an attendance record."
            )
            return

        attendance_id = selected[0]

        if messagebox.askyesno(
            "Confirm",
            "Delete selected attendance record?"
        ):
            try:
                if execute_query(
                    """
                    DELETE FROM attendance
                    WHERE attendance_id=%s
                    """,
                    (attendance_id,)
                ):
                    messagebox.showinfo(
                        "Success",
                        "Attendance record deleted successfully."
                    )

                self.load_attendance()
                self.update_dashboard()

            except Exception as error:
                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

    def load_attendance(self):
        rows = fetch_all(
            """
            SELECT
                attendance.attendance_id,
                students.name,
                attendance.attendance_date,
                attendance.status
            FROM attendance
            INNER JOIN students ON students.student_id = attendance.student_id
            ORDER BY attendance.attendance_date DESC,
                     attendance.attendance_id DESC
            """
        )

        self.clear_tree(self.attendance_tree)

        for display_id, row in enumerate(rows, start=1):
            self.attendance_tree.insert(
                "",
                tk.END,
                iid=str(row[0]),
                values=(display_id, *row[1:])
            )

    # =========================================================
    # MARKS MODULE
    # =========================================================

    def create_marks_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Marks")

        header = tk.Frame(
            tab,
            bg="#FFF7ED",
            highlightbackground="#FED7AA",
            highlightthickness=1
        )
        header.pack(
            fill="x",
            padx=15,
            pady=(15, 5)
        )

        tk.Label(
            header,
            text="Marks Management",
            bg="#FFF7ED",
            fg="#D97706",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(12, 2)
        )

        tk.Label(
            header,
            text="Enter and manage student examination marks",
            bg="#FFF7ED",
            fg=self.gray,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 12)
        )

        form = ttk.LabelFrame(
            tab,
            text="Enter Student Marks",
            padding=15
        )
        form.pack(
            fill="x",
            padx=15,
            pady=10
        )

        ttk.Label(
            form,
            text="Student ID"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.marks_student_id = ttk.Combobox(
            form,
            width=18,
            state="readonly"
        )
        self.marks_student_id.grid(
            row=1,
            column=0,
            padx=(0, 15),
            pady=6
        )
        self.refresh_marks_students()

        ttk.Label(
            form,
            text="Subject"
        ).grid(
            row=0,
            column=1,
            sticky="w"
        )

        self.marks_subject = ttk.Entry(
            form,
            width=25
        )
        self.marks_subject.grid(
            row=1,
            column=1,
            padx=15
        )

        ttk.Label(
            form,
            text="Marks (0 - 100)"
        ).grid(
            row=0,
            column=2,
            sticky="w"
        )

        self.marks_value = ttk.Entry(
            form,
            width=20
        )
        self.marks_value.grid(
            row=1,
            column=2,
            padx=15
        )

        self.create_button(
            form,
            "Save Marks",
            self.add_marks,
            self.marks_color
        ).grid(
            row=1,
            column=3,
            padx=10
        )

        self.create_button(
            form,
            "Clear",
            self.clear_marks,
            self.gray
        ).grid(
            row=1,
            column=4,
            padx=5
        )

        self.create_button(
            form,
            "Delete Selected",
            self.delete_marks,
            self.danger
        ).grid(
            row=1,
            column=5,
            padx=5
        )

        tk.Label(
            tab,
            text="Marks Records",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 3)
        )

        self.marks_tree = ttk.Treeview(
            tab,
            columns=("ID", "Student", "Subject", "Marks"),
            show="headings"
        )

        for column, width in zip(
            self.marks_tree["columns"],
            [100, 160, 280, 180]
        ):
            self.marks_tree.heading(
                column,
                text=column
            )
            self.marks_tree.column(
                column,
                width=width
            )

        self.marks_tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.load_marks()

    def add_marks(self):
        student_text = (
            self.marks_student_id
            .get()
            .strip()
        )

        if not student_text:
            messagebox.showwarning(
                "Missing Student ID",
                "Please enter Student ID."
            )
            return

        try:
            student_id = self.marks_student_map.get(student_text)
            if student_id is None:
                raise ValueError
            marks = float(
                self.marks_value
                .get()
                .strip()
            )
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Student ID must be an integer and marks must be a number."
            )
            return

        if not self.student_exists(student_id):
            messagebox.showerror(
                "Student Not Found",
                f"Student ID {student_id} does not exist."
            )
            return

        if marks < 0 or marks > 100:
            messagebox.showerror(
                "Invalid Marks",
                "Marks must be between 0 and 100."
            )
            return

        subject = (
            self.marks_subject
            .get()
            .strip()
        )

        if not subject:
            messagebox.showwarning(
                "Missing Subject",
                "Please enter subject."
            )
            return

        query = """
        INSERT INTO marks
        (student_id,subject,marks)
        VALUES (%s,%s,%s)
        """

        try:
            if execute_query(
                query,
                (
                    student_id,
                    subject,
                    marks
                )
            ):
                messagebox.showinfo(
                    "Success",
                    "Marks saved successfully."
                )

                self.clear_marks()
                self.load_marks()
                self.update_dashboard()

        except Exception as error:
            messagebox.showerror(
                "Marks Error",
                str(error)
            )

    def clear_marks(self):
        self.marks_student_id.delete(
            0,
            tk.END
        )

        self.marks_subject.delete(
            0,
            tk.END
        )

        self.marks_value.delete(
            0,
            tk.END
        )

    def delete_marks(self):
        selected = self.marks_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Record",
                "Please select a marks record."
            )
            return

        mark_id = selected[0]

        if messagebox.askyesno(
            "Confirm",
            "Delete selected marks record?"
        ):
            try:
                if execute_query(
                    """
                    DELETE FROM marks
                    WHERE mark_id=%s
                    """,
                    (mark_id,)
                ):
                    messagebox.showinfo(
                        "Success",
                        "Marks record deleted successfully."
                    )

                self.load_marks()
                self.update_dashboard()

            except Exception as error:
                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

    def load_marks(self):
        rows = fetch_all(
            """
            SELECT
                marks.mark_id,
                students.name,
                marks.subject,
                marks.marks
            FROM marks
            INNER JOIN students ON students.student_id = marks.student_id
            ORDER BY marks.mark_id DESC
            """
        )

        self.clear_tree(self.marks_tree)

        for display_id, row in enumerate(rows, start=1):
            self.marks_tree.insert(
                "",
                tk.END,
                iid=str(row[0]),
                values=(display_id, *row[1:])
            )

    # =========================================================
    # FEES MODULE
    # =========================================================

    def create_fees_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Fees")

        header = tk.Frame(
            tab,
            bg="#FFF7ED",
            highlightbackground="#FED7AA",
            highlightthickness=1
        )
        header.pack(
            fill="x",
            padx=15,
            pady=(15, 5)
        )

        tk.Label(
            header,
            text="Fees Management",
            bg="#FFF7ED",
            fg="#D97706",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(12, 2)
        )

        tk.Label(
            header,
            text="Record student fee payments and monitor payment status",
            bg="#FFF7ED",
            fg=self.gray,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 12)
        )

        form = ttk.LabelFrame(
            tab,
            text="Fee Payment",
            padding=15
        )
        form.pack(
            fill="x",
            padx=15,
            pady=10
        )

        ttk.Label(
            form,
            text="Student ID"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.fee_student_id = ttk.Combobox(
            form,
            width=18,
            state="readonly"
        )
        self.fee_student_id.grid(
            row=1,
            column=0,
            padx=(0, 15),
            pady=6
        )
        self.refresh_fee_students()

        ttk.Label(
            form,
            text="Amount"
        ).grid(
            row=0,
            column=1,
            sticky="w"
        )

        self.fee_amount = ttk.Entry(
            form,
            width=18
        )
        self.fee_amount.grid(
            row=1,
            column=1,
            padx=15
        )

        ttk.Label(
            form,
            text="Payment Date"
        ).grid(
            row=0,
            column=2,
            sticky="w"
        )

        self.fee_date = ttk.Entry(
            form,
            width=18
        )
        self.fee_date.insert(
            0,
            str(date.today())
        )
        self.fee_date.grid(
            row=1,
            column=2,
            padx=15
        )

        ttk.Label(
            form,
            text="Status"
        ).grid(
            row=0,
            column=3,
            sticky="w"
        )

        self.fee_status = ttk.Combobox(
            form,
            values=["Paid", "Pending"],
            state="readonly",
            width=15
        )
        self.fee_status.set("Paid")
        self.fee_status.grid(
            row=1,
            column=3,
            padx=15
        )

        self.create_button(
            form,
            "Save Fee",
            self.add_fee,
            self.fees_color
        ).grid(
            row=1,
            column=4,
            padx=10
        )

        self.create_button(
            form,
            "Clear",
            self.clear_fee,
            self.gray
        ).grid(
            row=1,
            column=5,
            padx=5
        )

        self.create_button(
            form,
            "Delete Selected",
            self.delete_fee,
            self.danger
        ).grid(
            row=1,
            column=6,
            padx=5
        )

        tk.Label(
            tab,
            text="Payment History",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 3)
        )

        self.fee_tree = ttk.Treeview(
            tab,
            columns=(
                "ID",
                "Student",
                "Amount",
                "Payment Date",
                "Status"
            ),
            show="headings"
        )

        for column, width in zip(
            self.fee_tree["columns"],
            [100, 160, 180, 220, 180]
        ):
            self.fee_tree.heading(
                column,
                text=column
            )
            self.fee_tree.column(
                column,
                width=width
            )

        self.fee_tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.load_fees()

    def add_fee(self):
        student_text = (
            self.fee_student_id
            .get()
            .strip()
        )

        if not student_text:
            messagebox.showwarning(
                "Missing Student ID",
                "Please enter Student ID."
            )
            return

        try:
            student_id = self.fee_student_map.get(student_text)
            if student_id is None:
                raise ValueError

            amount = float(
                self.fee_amount
                .get()
                .strip()
            )

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Student ID must be a number and amount must be valid."
            )
            return

        if not self.student_exists(student_id):
            messagebox.showerror(
                "Student Not Found",
                f"Student ID {student_id} does not exist."
            )
            return

        if amount <= 0:
            messagebox.showerror(
                "Invalid Amount",
                "Fee amount must be greater than zero."
            )
            return

        payment_date = (
            self.fee_date
            .get()
            .strip()
        )

        if not self.validate_date(payment_date):
            messagebox.showerror(
                "Invalid Date",
                "Please enter date in YYYY-MM-DD format."
            )
            return

        status = self.fee_status.get()

        query = """
        INSERT INTO fees
        (student_id,amount,payment_date,status)
        VALUES (%s,%s,%s,%s)
        """

        try:
            if execute_query(
                query,
                (
                    student_id,
                    amount,
                    payment_date,
                    status
                )
            ):
                messagebox.showinfo(
                    "Success",
                    "Fee record saved successfully."
                )

                self.clear_fee()
                self.load_fees()
                self.update_dashboard()

        except Exception as error:
            messagebox.showerror(
                "Fees Error",
                str(error)
            )

    def clear_fee(self):
        self.fee_student_id.delete(
            0,
            tk.END
        )

        self.fee_amount.delete(
            0,
            tk.END
        )

        self.fee_date.delete(
            0,
            tk.END
        )

        self.fee_date.insert(
            0,
            str(date.today())
        )

        self.fee_status.set("Paid")

    def delete_fee(self):
        selected = self.fee_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Record",
                "Please select a fee record."
            )
            return

        fee_id = selected[0]

        if messagebox.askyesno(
            "Confirm",
            "Delete selected fee record?"
        ):
            try:
                if execute_query(
                    """
                    DELETE FROM fees
                    WHERE fee_id=%s
                    """,
                    (fee_id,)
                ):
                    messagebox.showinfo(
                        "Success",
                        "Fee record deleted successfully."
                    )

                self.load_fees()
                self.update_dashboard()

            except Exception as error:
                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

    def load_fees(self):
        rows = fetch_all(
            """
            SELECT
                fees.fee_id,
                students.name,
                fees.amount,
                fees.payment_date,
                fees.status
            FROM fees
            INNER JOIN students ON students.student_id = fees.student_id
            ORDER BY fees.payment_date DESC,
                     fees.fee_id DESC
            """
        )

        self.clear_tree(self.fee_tree)

        for display_id, row in enumerate(rows, start=1):
            self.fee_tree.insert(
                "",
                tk.END,
                iid=str(row[0]),
                values=(display_id, *row[1:])
            )


# =============================================================
# REDESIGNED DASHBOARD
# =============================================================

    def create_dashboard_tab(self):
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")

        surface = tk.Frame(self.dashboard_tab, bg=self.bg)
        surface.pack(fill="both", expand=True, padx=4, pady=4)

        cards = tk.Frame(surface, bg=self.bg)
        cards.pack(fill="x", pady=(0, 12))
        self.dashboard_cards = {}

        card_info = [
            ("Total Students", "Students", "0", "#9337F3", "Live database count"),
            ("Total Teachers", "Teachers", "0", "#087BF2", "Live database count"),
            ("Total Courses", "Courses", "0", "#F07800", "Live database count"),
            ("Total Fees Collected", "Fee Records", "0", "#D7195C", "Live database total"),
            ("Attendance Records", "Attendance", "0", "#16B978", "Live database count"),
            ("Marks Records", "Marks", "0", "#E7A61A", "Live database count")
        ]

        for index, (title, key, value, color, change) in enumerate(card_info):
            card = tk.Frame(
                cards,
                bg="#102044",
                highlightbackground="#203563",
                highlightthickness=1
            )
            card.grid(row=0, column=index, padx=5, sticky="nsew")
            cards.columnconfigure(index, weight=1)

            tk.Frame(card, bg=color, height=4).pack(fill="x")
            tk.Label(
                card,
                text=title,
                bg="#102044",
                fg="#B6C2DF",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", padx=14, pady=(13, 2))

            value_label = tk.Label(
                card,
                text=value,
                bg="#102044",
                fg=self.white,
                font=("Segoe UI", 22, "bold")
            )
            value_label.pack(anchor="w", padx=14)
            self.dashboard_cards[key] = value_label

            tk.Label(
                card,
                text=change,
                bg="#102044",
                fg="#91A1C4",
                font=("Segoe UI", 8)
            ).pack(anchor="w", padx=14, pady=(2, 12))

        lower = tk.Frame(surface, bg=self.bg)
        lower.pack(fill="both", expand=True)
        lower.columnconfigure(0, weight=5)
        lower.columnconfigure(1, weight=3)
        lower.columnconfigure(2, weight=3)
        lower.rowconfigure(0, weight=1)
        lower.rowconfigure(1, weight=1)

        chart_panel = self.create_dashboard_panel(lower, "Attendance overview")
        chart_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 6), pady=4)

        legend = tk.Frame(chart_panel, bg="#102044")
        legend.pack(fill="x", padx=15, pady=(0, 4))
        tk.Label(legend, text="This week's attendance performance", bg="#102044", fg="#91A1C4", font=("Segoe UI", 9)).pack(side="left")

        self.dashboard_chart = tk.Canvas(chart_panel, height=205, bg="#102044", highlightthickness=0)
        self.dashboard_chart.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        attendance_panel = self.create_dashboard_panel(lower, "Today's attendance")
        attendance_panel.grid(row=0, column=1, sticky="nsew", padx=6, pady=4)
        attendance_canvas = tk.Canvas(attendance_panel, width=230, height=180, bg="#102044", highlightthickness=0)
        attendance_canvas.pack(pady=(12, 2))
        attendance_canvas.create_oval(28, 12, 202, 186, outline="#203B6E", width=17)
        self.attendance_canvas = attendance_canvas
        self.attendance_percent_text = attendance_canvas.create_text(115, 82, text="0%", fill=self.white, font=("Segoe UI", 28, "bold"))
        attendance_canvas.create_text(115, 116, text="Present today", fill="#B6C2DF", font=("Segoe UI", 10))
        self.present_label = tk.Label(attendance_panel, text="●  Present                 0", bg="#102044", fg="#27E36F", font=("Segoe UI", 10, "bold"))
        self.present_label.pack(anchor="w", padx=20, pady=(2, 2))
        self.absent_label = tk.Label(attendance_panel, text="●  Absent                   0", bg="#102044", fg="#F34D75", font=("Segoe UI", 10, "bold"))
        self.absent_label.pack(anchor="w", padx=20, pady=(2, 12))

        events_panel = self.create_dashboard_panel(lower, "Upcoming Events")
        events_panel.grid(row=0, column=2, sticky="nsew", padx=(6, 0), pady=4)
        event_form = tk.Frame(events_panel, bg="#102044")
        event_form.pack(fill="x", padx=10, pady=(2, 4))
        self.event_title = ttk.Entry(event_form, width=18)
        self.event_title.grid(row=0, column=0, padx=2, pady=2)
        self.event_date = ttk.Entry(event_form, width=12)
        self.event_date.grid(row=0, column=1, padx=2, pady=2)
        self.event_date.insert(0, str(date.today()))
        self.event_description = ttk.Entry(event_form, width=32)
        self.event_description.grid(row=1, column=0, columnspan=2, padx=2, pady=2, sticky="ew")
        event_form.columnconfigure(0, weight=1)
        self.create_button(event_form, "Add", self.add_event, self.success).grid(row=0, column=2, rowspan=2, padx=3)
        self.create_button(event_form, "Update", self.update_event, self.primary).grid(row=0, column=3, rowspan=2, padx=3)
        self.create_button(event_form, "Delete", self.delete_event, self.danger).grid(row=0, column=4, rowspan=2, padx=3)
        self.events_tree = ttk.Treeview(events_panel, columns=("ID", "Title", "Date", "Description"), show="headings", height=5)
        for column, width in [("ID", 35), ("Title", 100), ("Date", 85), ("Description", 145)]:
            self.events_tree.heading(column, text=column)
            self.events_tree.column(column, width=width, anchor="w")
        self.events_tree.pack(fill="both", expand=True, padx=10, pady=6)
        self.events_tree.bind("<<TreeviewSelect>>", self.select_event)

        recent_panel = self.create_dashboard_panel(lower, "Recent Students")
        recent_panel.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=(6, 0), pady=4)
        self.recent_tree = ttk.Treeview(recent_panel, columns=("ID", "Name", "Course", "Year"), show="headings", height=4)
        for column, width in [("ID", 45), ("Name", 130), ("Course", 90), ("Year", 65)]:
            self.recent_tree.heading(column, text=column)
            self.recent_tree.column(column, width=width, anchor="w")
        self.recent_tree.pack(fill="both", expand=True, padx=10, pady=8)

        actions = ttk.LabelFrame(surface, text="Quick Actions", padding=10)
        actions.pack(fill="x", pady=(8, 0))
        for text, index, color in [("Add Student", 1, self.student_color), ("Take Attendance", 4, self.attendance_color), ("Enter Marks", 5, self.marks_color), ("Record Fees", 6, self.fees_color)]:
            self.create_button(actions, text, lambda i=index: self.open_tab(i), color).pack(side="left", padx=5)

        self.load_recent_students()
        self.draw_attendance_chart([])
        self.update_attendance_summary(0, 0)

    def draw_attendance_chart(self, attendance_rows):
        chart = self.dashboard_chart
        chart.delete("all")
        chart.update_idletasks()
        width = max(chart.winfo_width(), 540)
        height = 225
        left = 42
        right = width - 16
        bottom = height - 25
        top = 18
        for value in (0, 50, 100):
            y = bottom - ((bottom - top) * value / 100)
            chart.create_line(left, y, right, y, fill="#203563")
            chart.create_text(8, y, text=f"{value}%", fill="#8192B8", font=("Segoe UI", 8), anchor="w")

        if not attendance_rows:
            chart.create_text(width / 2, height / 2, text="No attendance data available", fill="#8192B8", font=("Segoe UI", 10))
            return

        slot = (right - left) / max(len(attendance_rows) - 1, 1)
        points = []
        for index, (attendance_date, percentage) in enumerate(attendance_rows):
            x = left + slot * index
            y = bottom - (bottom - top) * min(float(percentage), 100) / 100
            points.append((x, y))
            chart.create_text(
                x, bottom + 12, text=str(attendance_date)[5:10],
                fill="#8192B8", font=("Segoe UI", 8)
            )

        if len(points) > 1:
            chart.create_polygon(
                points + [(points[-1][0], bottom), (points[0][0], bottom)],
                fill="#123C52", outline=""
            )
            chart.create_line(points, fill="#27E896", width=4, smooth=True)
        for x, y in points:
            chart.create_oval(x - 7, y - 7, x + 7, y + 7, fill="#27E896", outline="#D8FFF0", width=2)

        chart.create_oval(right - 112, top, right - 100, top + 12, fill="#27E896", outline="")
        chart.create_text(right - 94, top + 6, text="Present", fill="#B6C2DF", font=("Segoe UI", 9), anchor="w")

    def ensure_events_table(self):
        execute_query(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(100) NOT NULL,
                event_date DATE NOT NULL,
                description VARCHAR(255)
            )
            """
        )

    def add_event(self):
        title = self.event_title.get().strip()
        event_date = self.event_date.get().strip()
        description = self.event_description.get().strip()
        if not title or not self.validate_date(event_date):
            messagebox.showwarning("Invalid Event", "Enter an event title and date in YYYY-MM-DD format.")
            return
        if execute_query(
            "INSERT INTO events (title, event_date, description) VALUES (%s, %s, %s)",
            (title, event_date, description)
        ):
            self.clear_event()
            self.load_events()

    def update_event(self):
        selected = self.events_tree.selection()
        if not selected:
            messagebox.showwarning("Select Event", "Select an event to update.")
            return
        if execute_query(
            "UPDATE events SET title=%s, event_date=%s, description=%s WHERE event_id=%s",
            (self.event_title.get().strip(), self.event_date.get().strip(), self.event_description.get().strip(), selected[0])
        ):
            self.clear_event()
            self.load_events()

    def delete_event(self):
        selected = self.events_tree.selection()
        if not selected:
            messagebox.showwarning("Select Event", "Select an event to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete this upcoming event?"):
            if execute_query("DELETE FROM events WHERE event_id=%s", (selected[0],)):
                self.clear_event()
                self.load_events()

    def select_event(self, event=None):
        selected = self.events_tree.selection()
        if not selected:
            return
        values = self.events_tree.item(selected[0])["values"]
        self.event_title.delete(0, tk.END)
        self.event_title.insert(0, values[1])
        self.event_date.delete(0, tk.END)
        self.event_date.insert(0, values[2])
        self.event_description.delete(0, tk.END)
        self.event_description.insert(0, values[3])

    def clear_event(self):
        self.event_title.delete(0, tk.END)
        self.event_date.delete(0, tk.END)
        self.event_date.insert(0, str(date.today()))
        self.event_description.delete(0, tk.END)

    def load_events(self):
        if not hasattr(self, "events_tree"):
            return
        self.clear_tree(self.events_tree)
        rows = fetch_all(
            "SELECT event_id, title, event_date, COALESCE(description, '') FROM events ORDER BY event_date ASC, event_id ASC LIMIT 6"
        )
        for row in rows:
            self.events_tree.insert("", tk.END, iid=str(row[0]), values=row)

    def update_attendance_summary(self, present, absent):
        total = present + absent
        percentage = round((present / total) * 100) if total else 0
        self.attendance_canvas.itemconfigure(self.attendance_percent_text, text=f"{percentage}%")
        self.present_label.config(text=f"●  Present     {present}")
        self.absent_label.config(text=f"●  Absent         {absent}")
        self.attendance_canvas.delete("progress")
        if total:
            self.attendance_canvas.create_arc(
                28, 12, 202, 186,
                start=90,
                extent=-(percentage * 3.6),
                outline="#27E36F",
                width=17,
                tags="progress"
            )

    def create_dashboard_panel(self, parent, title):
        panel = tk.Frame(parent, bg="#102044", highlightbackground="#203563", highlightthickness=1)
        tk.Label(panel, text=title, bg="#102044", fg=self.white, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=15, pady=(12, 4))
        return panel

    def load_recent_students(self):
        if not hasattr(self, "recent_tree"):
            return
        self.clear_tree(self.recent_tree)
        rows = fetch_all("SELECT student_id,name,course,year FROM students ORDER BY student_id DESC LIMIT 4")
        for display_id, row in enumerate(rows, start=1):
            self.recent_tree.insert(
                "",
                tk.END,
                values=(display_id, *row[1:])
            )


class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("PRMCEAM - Login")
        self.root.geometry("460x430")
        self.root.minsize(420, 390)
        self.root.configure(bg="#081431")
        self.app = None

        self.ensure_users_table()

        self.background_image = None
        background_path = os.path.join(os.path.dirname(__file__), "assets", "library.jpg")
        if Image and os.path.isfile(background_path):
            background = Image.open(background_path).resize((460, 430))
            self.background_image = ImageTk.PhotoImage(background)
            tk.Label(root, image=self.background_image, borderwidth=0).place(
                relx=0, rely=0, relwidth=1, relheight=1
            )

        card = tk.Frame(root, bg="#102044", highlightbackground="#203563", highlightthickness=1)
        card.place(relx=0.5, rely=0.42, anchor="center", relwidth=0.8, relheight=0.82)

        tk.Label(card, text="PRMCEAM", bg="#102044", fg="#E83E9F", font=("Segoe UI", 25, "bold")).pack(pady=(35, 3))
        tk.Label(card, text="College Management System", bg="#102044", fg="#B6C2DF", font=("Segoe UI", 11)).pack(pady=(0, 28))

        tk.Label(card, text="Username", bg="#102044", fg="#F8FAFF", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=55)
        self.username = ttk.Entry(card, width=31)
        self.username.pack(padx=55, pady=(5, 15), ipady=5)

        tk.Label(card, text="Password", bg="#102044", fg="#F8FAFF", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=55)
        self.password = ttk.Entry(card, width=31, show="*")
        self.password.pack(padx=55, pady=(5, 20), ipady=5)
        self.username.bind("<Return>", lambda event: self.password.focus_set())
        self.password.bind("<Return>", lambda event: self.login())

        self.login_button = tk.Button(card, text="Login", command=self.login, bg="#7044F5", fg="white", activebackground="#5430C9", activeforeground="white", relief="flat", bd=0, font=("Segoe UI", 10, "bold"), padx=35, pady=9, cursor="hand2")
        self.login_button.pack()
        self.status_label = tk.Label(card, text="Enter your account credentials", bg="#102044", fg="#91A1C4", font=("Segoe UI", 8))
        self.status_label.pack(pady=(22, 0))

        self.login_button.bind("<Enter>", lambda event: self.login_button.configure(bg="#855FFF"))
        self.login_button.bind("<Leave>", lambda event: self.login_button.configure(bg="#7044F5"))
        self.animate_login(card)

        self.username.focus_set()

    def animate_login(self, card, step=0):
        """Ease the login card into place when the window opens."""
        progress = min(step / 12, 1)
        eased = 1 - (1 - progress) ** 3
        card.place_configure(rely=0.42 + (0.08 * eased))
        try:
            self.root.attributes("-alpha", 0.35 + (0.65 * eased))
        except tk.TclError:
            pass
        if progress < 1:
            self.root.after(25, lambda: self.animate_login(card, step + 1))

    def hash_password(self, password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def ensure_users_table(self):
        execute_query(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash CHAR(64) NOT NULL
            )
            """
        )
        username = "Ayushpawar"
        password_hash = self.hash_password("Ayushpawar01")
        if not fetch_all("SELECT user_id FROM users WHERE username=%s", (username,)):
            execute_query(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
        else:
            execute_query(
                "UPDATE users SET password_hash=%s WHERE username=%s",
                (password_hash, username)
            )

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()
        if not username or not password:
            self.status_label.configure(text="Username and password are required.", fg="#F59E0B")
            messagebox.showwarning("Login Required", "Enter both username and password.")
            return

        connection = get_connection()
        if connection is None:
            users = [(1,)] if username == "Ayushpawar" and password == "Ayushpawar01" else []
        else:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "SELECT user_id FROM users WHERE username=%s AND password_hash=%s",
                    (username, self.hash_password(password))
                )
                users = cursor.fetchall()
            finally:
                cursor.close()
                connection.close()

        if not users:
            self.password.delete(0, tk.END)
            self.status_label.configure(text="Login failed. Check your credentials.", fg="#EF4444")
            messagebox.showerror("Login Failed", "Invalid username or password.")
            return

        for child in self.root.winfo_children():
            child.destroy()
        CollegeManagementSystem(self.root)


# =============================================================
# START APPLICATION
# =============================================================

if __name__ == "__main__":
    root = tk.Tk()
    LoginScreen(root)
    root.mainloop()
