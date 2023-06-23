"""Interaction with SQLite database.
"""
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY


class SQLiteAccess:
    """Class handling SQLite connection and writes"""

    # TODO This should not be a class, a fully functional approach is better

    def __init__(self):
        try:
            self.db_location = os.environ["FASTAPI_SIMPLE_SECURITY_DB_LOCATION"]
        except KeyError:
            self.db_location = "sqlite.db"

        try:
            self.expiration_limit = int(
                os.environ["FAST_API_SIMPLE_SECURITY_AUTOMATIC_EXPIRATION"]
            )
        except KeyError:
            self.expiration_limit = 15

        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()
            # Create database
            c.execute(
                """
        CREATE TABLE IF NOT EXISTS fastapi_simple_security (
            api_key TEXT PRIMARY KEY,
            is_active INTEGER,
            never_expire INTEGER,
            expiration_date TEXT,
            latest_query_date TEXT,
            total_queries INTEGER)
        """
            )
            connection.commit()
            # Migration: Add api key name
            try:
                c.execute("ALTER TABLE fastapi_simple_security ADD COLUMN name TEXT")
                connection.commit()
            except sqlite3.OperationalError:
                pass  # Column already exist

    def create_key(self, name, never_expire) -> str:
        api_key = str(uuid.uuid4())

        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()
            c.execute(
                """
                INSERT INTO fastapi_simple_security
                (api_key, is_active, never_expire, expiration_date, \
                    latest_query_date, total_queries, name)
                VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    api_key,
                    1,
                    1 if never_expire else 0,
                    (
                        datetime.utcnow() + timedelta(days=self.expiration_limit)
                    ).isoformat(timespec="seconds"),
                    None,
                    0,
                    name,
                ),
            )
            connection.commit()

        return api_key

    def renew_key(self, api_key: str, new_expiration_date: str) -> Optional[str]:
        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()

            # We run the query like check_key but will use the response differently
            c.execute(
                """
            SELECT is_active, total_queries, expiration_date, never_expire
            FROM fastapi_simple_security
            WHERE api_key = ?""",
                (api_key,),
            )

            response = c.fetchone()

            # API key not found
            if not response:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND, detail="API key not found"
                )

            response_lines = []

            # Previously revoked key. Issue a text warning and reactivate it.
            if response[0] == 0:
                response_lines.append(
                    "This API key was revoked and has been reactivated."
                )

            # Without an expiration date, we set it here
            if not new_expiration_date:
                parsed_expiration_date = (
                    datetime.utcnow() + timedelta(days=self.expiration_limit)
                ).isoformat(timespec="seconds")

            else:
                try:
                    # We parse and re-write to the right timespec
                    parsed_expiration_date = datetime.fromisoformat(
                        new_expiration_date
                    ).isoformat(timespec="seconds")
                except ValueError as exc:
                    raise HTTPException(
                        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="The expiration date could not be parsed. \
                            Please use ISO 8601.",
                    ) from exc

            c.execute(
                """
            UPDATE fastapi_simple_security
            SET expiration_date = ?, is_active = 1
            WHERE api_key = ?
            """,
                (
                    parsed_expiration_date,
                    api_key,
                ),
            )

            connection.commit()

            response_lines.append(
                f"The new expiration date for the API key is {parsed_expiration_date}"
            )

            return " ".join(response_lines)

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
                (api_key,),
            )

            connection.commit()

    def check_key(self, api_key: str) -> bool:
        """
        Checks if an API key is valid

        Args:
             api_key: the API key to validate
        """

        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()

            c.execute(
                """
            SELECT is_active, total_queries, expiration_date, never_expire
            FROM fastapi_simple_security
            WHERE api_key = ?""",
                (api_key,),
            )

            response = c.fetchone()

            if (
                # Cannot fetch a row
                not response
                # Inactive
                or response[0] != 1
                # Expired key
                or (
                    (not response[3])
                    and (datetime.fromisoformat(response[2]) < datetime.utcnow())
                )
            ):
                # The key is not valid
                return False
            else:
                # The key is valid

                # We run the logging in a separate thread as writing takes some time
                threading.Thread(
                    target=self._update_usage,
                    args=(
                        api_key,
                        response[1],
                    ),
                ).start()

                # We return directly
                return True

    def _update_usage(self, api_key: str, usage_count: int):
        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()

            # If we get there, this means it’s an active API key that’s in the database
            #   We update the table
            c.execute(
                """
            UPDATE fastapi_simple_security
            SET total_queries = ?, latest_query_date = ?
            WHERE api_key = ?
            """,
                (
                    usage_count + 1,
                    datetime.utcnow().isoformat(timespec="seconds"),
                    api_key,
                ),
            )

            connection.commit()

    def get_usage_stats(self) -> List[Tuple[str, bool, bool, str, str, int]]:
        """
        Returns usage stats for all API keys

        Returns:
            a list of tuples with values being api_key, is_active, expiration_date, \
                latest_query_date, and total_queries
        """
        with sqlite3.connect(self.db_location) as connection:
            c = connection.cursor()

            c.execute(
                """
            SELECT api_key, is_active, never_expire, expiration_date, \
                latest_query_date, total_queries, name
            FROM fastapi_simple_security
            ORDER BY latest_query_date DESC
            """,
            )

            response = c.fetchall()

        return response


sqlite_access = SQLiteAccess()
