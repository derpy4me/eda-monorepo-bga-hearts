"""SurrealDB integration library for the BGA Cheat Engine.

This module provides functionality for connecting to and interacting with a SurrealDB
database, specifically for archiving raw log data from the BGA system.
"""

# Standard Library Imports
from typing import Dict, Any, Callable, Coroutine
import logging

# Third Party Imports
from surrealdb import RecordID
from uuid_utils.compat import uuid7

# Local App Imports
from bce.surreal_connection_manager_lib import SurrealConnection


class SurrealDBManager:
    """Manages the connection and data writing operations for a SurrealDB instance.

    This class provides methods for connecting to a SurrealDB database, executing queries,
    and performing CRUD operations on records.
    """

    def __init__(self, connect_func: Callable[[], Coroutine[None, None, SurrealConnection]]):
        """Initializes the manager with connection details.

        Connection details are read from environment variables with fallback defaults.
        It's recommended to use environment variables for production deployments.
        """
        self.conn_func = connect_func
        self.conn = None

    async def connect(self):
        """Establishes a connection to the SurrealDB instance and signs in.

        Connects to the SurrealDB instance using the configured URL, authenticates with
        the provided credentials, and selects the namespace and database.

        Raises:
            Exception: If connection or authentication fails.
        """
        try:
            self.conn = await self.conn_func()
        except Exception as e:
            logging.error(f"Error connecting to SurrealDB: {e}")
            raise

    async def close(self):
        """Closes the SurrealDB connection.

        Properly terminates the connection to the SurrealDB instance and
        prints a confirmation message.
        """
        await self.conn.close()
        logging.info("SurrealDB connection closed.")

    async def archive_raw_log(self, log_data: Dict[str, Any]):
        """Archives a single raw log message into the 'raw_logs' table.

        Args:
            log_data (Dict[str, Any]): A dictionary representing the raw message from Kafka.

        Returns:
            Dict[str, Any]: The created record if successful, or an error dictionary containing
                the error message if the operation fails.

        Raises:
            Exception: Caught internally and returned as an error dictionary.
        """
        try:
            # The `create` method inserts the dictionary as a new record.
            # SurrealDB will automatically assign a unique ID.
            created = await self.conn.create(RecordID("raw_logs", uuid7()), log_data)
            return created
        except Exception as e:
            logging.error(f"Error archiving log to SurrealDB: {e}")
            return {"error": str(e)}

    async def query(self, query: str, params: dict | None = None) -> list[dict[str, Any]]:
        """Executes a custom SurrealQL query.

        Args:
            query (str): The SurrealQL query string to execute.
            params (dict | None, optional): Parameters to use in the query. Defaults to None.

        Returns:
            list[dict[str, Any]]: The query results as a list of dictionaries, or an empty list if an error occurs.

        Raises:
            Exception: Caught internally and logged. Returns an empty list on error.
        """
        try:
            response = await self.conn.query(query, params)
            return response
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return []

    async def delete_records_by_ids(self, record_ids: list[RecordID]):
        """Deletes a list of records by their IDs.

        Args:
            record_ids (list[RecordID]): A list of full record IDs (e.g., 'raw_logs:xyz').

        Returns:
            None: This method doesn't return any value.

        Raises:
            Exception: Caught internally and logged.
        """
        if not record_ids:
            return

        # Using a parameterized query to safely delete multiple records.
        # SurrealQL allows deleting multiple records in a single statement.
        query = "DELETE $ids RETURN BEFORE;"
        try:
            results = await self.conn.query(query, {"ids": record_ids})
            logging.debug(f"Successfully deleted {len(results)} records.")
        except Exception as e:
            logging.error(f"Error deleting records: {e}")

    async def __aenter__(self):
        """Asynchronous context manager entry.

        Establishes a connection to the SurrealDB instance when used in an async with statement.

        Returns:
            SurrealDBManager: The connected manager instance.
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronous context manager exit.

        Closes the connection to the SurrealDB instance when exiting an async with statement.

        Args:
            exc_type: The exception type if an exception was raised in the with block, otherwise None.
            exc_val: The exception value if an exception was raised in the with block, otherwise None.
            exc_tb: The traceback if an exception was raised in the with block, otherwise None.

        Returns:
            None: This method doesn't return any value.
        """
        await self.close()


async def test_surreal_connect():
    """Test the SurrealDB connection functionality.

    This function creates a SurrealDBManager instance and tests the connection
    to the SurrealDB database using the async context manager.

    This is primarily used for testing and debugging purposes.

    Returns:
        None: This function doesn't return any value.

    Raises:
        Exception: If connection to SurrealDB fails.
    """
    async with SurrealDBManager() as db:
        await db.connect()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_surreal_connect())
