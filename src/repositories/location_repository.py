import logging
from uuid import UUID
from ..database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

class LocationRepository:
    def __init__(self):
        self.db = DatabaseConnection.get_instance()

    def create_location(self, request_id: str, location: str, status: str) -> bool:
        conn = self.db.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO requests (id, location, status) VALUES (%s, %s, %s)",
                    (request_id, location, status)
                )
                conn.commit()
                return True
            except Exception as error:
                logger.error(f"Error in create_location: {error}")
                return False
            finally:
                cursor.close()
                self.db.return_connection(conn)
        return False

    def update_response_time(self, request_id: str, response_time: float) -> bool:
        conn = self.db.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE requests SET response_time = %s WHERE id = %s",
                    (response_time, request_id)
                )
                conn.commit()
                return True
            except Exception as error:
                logger.error(f"Error in update_response_time: {error}")
                return False
            finally:
                cursor.close()
                self.db.return_connection(conn)
        return False

    def get_location(self, request_id: str):
        conn = self.db.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, location, status, created_at, updated_at, response_time FROM requests WHERE id = %s",
                    (request_id,)
                )
                return cursor.fetchone()
            except Exception as error:
                logger.error(f"Error in get_location: {error}")
                return None
            finally:
                cursor.close()
                self.db.return_connection(conn)
        return None 