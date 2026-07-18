import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jurisdictions (
            name TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            status TEXT NOT NULL,
            verified_date TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_jurisdiction(name: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data, status, verified_date FROM jurisdictions WHERE name = %s", (name,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    data_str, status, verified_date = row
    data = json.loads(data_str)
    data["status"] = status
    data["verified_date"] = verified_date
    return data


def save_draft(name: str, data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jurisdictions (name, data, status, verified_date)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (name) DO UPDATE
        SET data = EXCLUDED.data, status = EXCLUDED.status, verified_date = EXCLUDED.verified_date
    """, (name, json.dumps(data), "pending", None))
    conn.commit()
    conn.close()


def approve(name: str, corrected_data: dict = None):
    conn = get_connection()
    cursor = conn.cursor()
    verified_date = __import__("datetime").datetime.now().isoformat()

    if corrected_data is not None:
        cursor.execute(
            "UPDATE jurisdictions SET data = %s, status = %s, verified_date = %s WHERE name = %s",
            (json.dumps(corrected_data), "verified", verified_date, name)
        )
    else:
        cursor.execute(
            "UPDATE jurisdictions SET status = %s, verified_date = %s WHERE name = %s",
            ("verified", verified_date, name)
        )
    conn.commit()
    conn.close()


def demote(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jurisdictions SET status = %s, verified_date = %s WHERE name = %s",
                   ("pending", None, name))
    conn.commit()
    conn.close()


def delete_jurisdiction(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jurisdictions WHERE name = %s", (name,))
    conn.commit()
    conn.close()


def list_pending() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, data, status, verified_date FROM jurisdictions WHERE status = %s", ("pending",))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for name, data_str, status, verified_date in rows:
        data = json.loads(data_str)
        data["name"] = name
        data["status"] = status
        data["verified_date"] = verified_date
        results.append(data)
    return results


def list_verified() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, data, status, verified_date FROM jurisdictions WHERE status = %s", ("verified",))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for name, data_str, status, verified_date in rows:
        data = json.loads(data_str)
        data["name"] = name
        data["status"] = status
        data["verified_date"] = verified_date
        results.append(data)
    return results

if __name__ == "__main__":
    init_db()
    print("connected and table created successfully")