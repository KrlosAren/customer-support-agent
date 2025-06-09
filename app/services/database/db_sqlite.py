import sqlite3


class DbSqlite:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        import sqlite3

        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        conn.commit()
        return cursor.fetchall()

    def close(self, conn):
        conn.close()
