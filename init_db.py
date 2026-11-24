import sqlite3 
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "helpdesk.db"

def init_db(db_path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_code TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            credits REAL NOT NULL,
            prerequisites TEXT NOT NULL DEFAULT 'None',
            department TEXT NOT NULL
        ); 
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sections (
            section_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            section_code TEXT NOT NULL,
            schedule TEXT NOT NULL,
            room TEXT NOT NULL,
            instructor TEXT NOT NULL,
            seats_remaining INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (course_code) REFERENCES courses(course_code)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            details TEXT NOT NULL,
            effective_date TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_query TEXT NOT NULL,
            matched_topic TEXT,
            escalated INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eval_dataset (
            eval_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            expected_answer TEXT NOT NULL,
            category TEXT NOT NULL,
            in_scope INTEGER NOT NULL DEFAULT 1
        );
    """)

    courses_seed = [
        ("ITEC 4020", "Internet Client-Server Systems", 3.0, "ITEC 3020", "Information Technology"),
        ("ITEC 3040", "Data Mining and Analytics", 3.0, "ITEC 2010", "Information Technology"),
        ("ITEC 3020", "Web Technologies", 3.0, "ITEC 1010", "Information Technology"),
    ]

    sections_seed = [
        ("ITEC 4020", "A", "Tuesdays 19:00-22:00", "LAS 1004", "Dr. Bhuiyan", 12),
        ("ITEC 4020", "B", "Wednesdays 14:30-17:30", "TEL 2006", "Dr. Bhuiyan", 0),
        ("ITEC 3040", "A", "Thursdays 14:30-17:30", "TEL 2006", "Prof. Patel", 8),
    ]

    policies_seed = [
        ("Enrollment",
            "Course Add / Drop Deadline",
            "Students can add or drop courses through the registration system up to the published term add/drop deadline without academic penalty.",
            "2026-09-01",),
        ("Tuition",
            "Refund Schedule Tiers",
            "Tuition refund percentages depend on the withdrawal date relative to the start of classes; late withdrawals may result in partial or zero refund.",
            "2026-09-01",),
        ("Exams",
            "Deferred Standing Agreement",
            "Students who miss a final exam due to documented medical or extenuating circumstances must submit a petition and supporting documentation promptly.",
            "2026-09-01",),
    ]

    eval_seed = [
        ("What are the prerequisites and schedule for ITEC 4020 Section A?",
            "ITEC 4020 requires ITEC 3020, and Section A meets Tuesdays 19:00-22:00 in LAS 1004 with 12 seats remaining.",
            "Course & Timetable",
            1,),
        ("Are there any seats left in ITEC 4020 Section B?",
            "No, ITEC 4020 Section B currently shows 0 seats remaining.",
            "Course & Timetable",
            1,),
        ("What is the rule for missing a final exam?",
            "Students who miss a final exam due to documented medical or extenuating circumstances must submit a petition and supporting documentation promptly.",
            "Policies",
            1,),
        ("Can you order me pizza to Lassonde Building?",
            "Out of scope: I can only help with course schedules, prerequisites, academic policies, and help desk tickets.",
            "Out of Scope",
            0,),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO courses (course_code, title, credits, prerequisites, department)
        VALUES (?,?,?,?,?);
        """,
        courses_seed,
    )

    existing_sections = cursor.execute("SELECT COUNT(*) FROM sections;").fetchone()[0]
    if existing_sections == 0:
        cursor.executemany(
            """
            INSERT INTO sections (course_code, section_code, schedule, room, instructor, seats_remaining)
            VALUES(?,?,?,?,?,?);
            """,
            sections_seed,
        )

    existing_policies = cursor.execute("SELECT COUNT(*) FROM policies;").fetchone()[0]
    if existing_policies == 0:
        cursor.executemany(
            """
            INSERT INTO policies (category, title, details, effective_date)
            VALUES(?,?,?,?)
            """,
            policies_seed,
        )

    existing_eval = cursor.execute("SELECT COUNT(*) FROM eval_dataset").fetchone()[0]
    if existing_eval == 0:
        cursor.executemany(
            """
            INSERT INTO eval_dataset(question, expected_answer, category, in_scope)
            VALUES(?,?,?,?)
            """,
            eval_seed,
        )

    conn.commit()
    conn.close()
    print(f"Initialized database successfully at: {db_path}")

if __name__ == "__main__":
    init_db()