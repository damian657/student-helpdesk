import sqlite3
from pathlib import Path
from typing import Any 

DB_PATH = Path(__file__).resolve().parent / "helpdesk.db"

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_course_with_sections(course_code: str, db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    code = course_code.strip().upper()
    query = """
        SELECT
            c.course_code,
            c.title,
            c.credits,
            c.prerequisites,
            c.department,
            s.section_id,
            s.schedule,
            s.room,
            s.instructor,
            s.seats_remaining
        FROM courses c
        LEFT JOIN sections s ON c.course_code = s.course_code
        WHERE UPPER(c.course_code) = ?
        ORDER BY s.section_code ASC;
    """
    with get_connection(db_path) as conn:
        rows = conn.execute(query, (code,)).fetchall()
    return [dict(row) for row in rows]

def search_policies(keyword: str = "", db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    cleaned = f"%{keyword.strip()}%"
    query = """
        SELECT policy_id, category, title, details, effective_date
        FROM policies
        WHERE title LIKE ? OR details LIKE ? OR CATEGORY LIKE ? 
        ORDER BY policy_id ASC;
    """
    with get_connection(db_path) as conn:
        rows = conn.execute(query, (cleaned, cleaned, cleaned)).fetchall()
    return[dict(row) for row in rows]

def create_ticket(
    student_query: str,
    matched_topic: str | None = None,
    escalated: bool = False,
    status: str = "Open",
    db_path: Path = DB_PATH,
) -> int: 
    query = """
        INSERT INTO tickets (student_query, matched_topic, escalated, status)
        VALUES (?,?,?,?);
    """
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            query,
            (student_query.strip(), matched_topic, int(escalated), status),
        )
        conn.commit()
        return int(cursor.lastrowid)
        
def get_eval_dataset(in_scope_only: bool = False, db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    query = "SELECT eval_id, question, expected_answer, category, in_scope FROM eval_dataset"
    if in_scope_only:
        query += " WHERE in_scope = 1"
    query += " ORDER BY eval_id ASC;"

    with get_connection(db_path) as conn:
        rows = conn.execute(query).fetchall()
    return[dict(row) for row in rows]

if __name__ == "__main__":
    print("--- ITEC 4020 Sections (JOIN) ---") 
    for item in get_course_with_sections("ITEC 4020"):
        print(item)

    print("\n--- Exam Policies ---")
    for pol in search_policies("exam"):
        print(pol)

    print("\n--- Eval Questions ---")
    for ev in get_eval_dataset():
        print(ev)