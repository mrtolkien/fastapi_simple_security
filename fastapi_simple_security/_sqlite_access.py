import sqlite3
import os
import uuid
from datetime import datetime
from typing import List, Tuple


class SQLiteAccess:
    def __init__(self):
        try:
            self.db_location = os.environ["FASTAPI_SIMPLE_SECURITY_DB_LOCATION"]
        except KeyError:
            self.db_location = "/app/sqlite.db"

    def init_db(self):
        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()
            c.execute(
                """
        CREATE TABLE IF NOT EXISTS fastapi_simple_security (
            api_key TEXT PRIMARY KEY,
            is_active INTEGER,
            creation_date TEXT,
            latest_query_date TEXT,
            total_queries INTEGER)
        """
            )
            connection.commit()

    def create_key(self) -> str:
        api_key = str(uuid.uuid4())

        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()
            c.execute(
                """
                INSERT INTO fastapi_simple_security 
                (api_key, is_active, creation_date, latest_query_date, total_queries) 
                VALUES(?, ?, ?, ?, ?)
            """,
                (api_key, 1, datetime.utcnow().isoformat(timespec="seconds"), None, 0),
            )
            connection.commit()

        return api_key

    def revoke_key(self, api_key: str):
        """
        Revokes an API key

        Args:
            api_key: the API key to revoke
        """
        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()

            c.execute(
                """
            UPDATE fastapi_simple_security
            SET is_active = 0
            WHERE api_key = ?
            """,
                [api_key],
            )

            connection.commit()

    def check_key(self, api_key: str) -> bool:
        """
        Checks if an API key is valid

        Args:
             api_key: the API key to validate
        """
        # TODO Add automatic expiration for older keys through an environment variable

        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()

            c.execute(
                """
            SELECT is_active, total_queries, creation_date 
            FROM fastapi_simple_security 
            WHERE api_key = ?""",
                [api_key],
            )

            response = c.fetchone()

            # If we cannot fetch a row or is_active is not 1, we return False
            if not response or response[0] != 1:
                return False

            # If we get there, this means it’s an active API key that’s in the database. We update the table.
            c.execute(
                """
            UPDATE fastapi_simple_security
            SET total_queries = ?, latest_query_date = ?
            WHERE api_key = ?
            """,
                (response[1] + 1, datetime.utcnow().isoformat(timespec="seconds"), api_key),
            )

            return True

    def get_usage_stats(self) -> List[Tuple[str, int, str, str, int]]:
        """
        Returns usage stats for all API keys

        Returns:
            a list of tuples with values being api_key, is_active, creation_date, latest_query_date, and total_queries
        """
        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()

            # TODO Add filtering on age of API key?
            c.execute(
                """
            SELECT api_key, is_active, creation_date, latest_query_date, total_queries 
            FROM fastapi_simple_security
            ORDER BY latest_query_date DESC
            """,
            )

            response = c.fetchall()

        return response


sqlite_access = SQLiteAccess()
