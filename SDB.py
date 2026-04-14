import sqlite3
import sys
import os


def get_db_path():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "database.db"


def print_results(cursor):
    rows = cursor.fetchall()
    if not rows:
        print(f"(no rows returned, {cursor.rowcount} row(s) affected)")
        return

    headers = [desc[0] for desc in cursor.description]
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_row = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"

    print(sep)
    print(header_row)
    print(sep)
    for row in rows:
        print("| " + " | ".join(str(v).ljust(col_widths[i]) for i, v in enumerate(row)) + " |")
    print(sep)
    print(f"({len(rows)} row(s))")


def run_query(conn, sql):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)

        if cursor.description:
            print_results(cursor)
        else:
            conn.commit()
            print(f"OK ({cursor.rowcount} row(s) affected)")
    except sqlite3.Error as e:
        print(f"Error: {e}")


def main():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    print(f"SDB - Simple Database")
    print(f"Connected to: {os.path.abspath(db_path)}")
    print("Type SQL queries, or:")
    print("  .tables    — list all tables")
    print("  .schema    — show schema for all tables")
    print("  .exit      — quit")
    print()

    buffer = []

    while True:
        prompt = "sdb> " if not buffer else "   > "
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        stripped = line.strip()

        if not buffer and stripped.startswith("."):
            if stripped == ".exit":
                break
            elif stripped == ".tables":
                run_query(conn, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            elif stripped == ".schema":
                run_query(conn, "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type, name")
            else:
                print(f"Unknown command: {stripped}")
            continue

        buffer.append(line)
        combined = " ".join(buffer).strip()

        if combined.endswith(";"):
            run_query(conn, combined)
            buffer = []

    conn.close()
    print("Bye.")


if __name__ == "__main__":
    main()
