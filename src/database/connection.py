import logging
import os

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    _pool = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Don't initialize the pool in __init__ to avoid immediate connection
        pass

    def _initialize_pool(self):
        if self._pool is not None or os.getenv('TESTING') == 'true':
            return

        try:
            import psycopg2
            from psycopg2 import pool

            config = {
                'dbname': "fastapi_db",
                'user': "fastapi_user",
                'password': "securepassword",
                'host': "postgres-service",
                'port': "5432"
            }

            self._pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **config
            )
            if self._pool:
                logger.info("Connection pool created successfully")
                self._create_table()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error while connecting to PostgreSQL: {error}")
            raise

    def _create_table(self):
        if os.getenv('TESTING') == 'true':
            return
            
        conn = self._pool.getconn()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id UUID PRIMARY KEY,
                    location TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    response_time FLOAT
                )
                """)
                conn.commit()
                cursor.close()
            except Exception as error:
                logger.error(f"Error creating table: {error}")
            finally:
                self._pool.putconn(conn)

    def get_connection(self):
        if os.getenv('TESTING') == 'true':
            return None
        self._initialize_pool()
        return self._pool.getconn() if self._pool else None

    def return_connection(self, conn):
        if os.getenv('TESTING') == 'true' or not self._pool:
            return
        if conn:
            self._pool.putconn(conn) 
