import psycopg2
from psycopg2 import pool
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
        if self._pool is None:
            try:
                # Get database configuration from environment variables
                dbname = os.getenv("postgres-db")
                user = os.getenv("postgres-user")
                password = os.getenv("postgres-password")
                host = os.getenv("postgres-service")
                port = os.getenv("postgres-port")

                # Log the values (without password for security)
                logger.info(f"Database configuration: host={host}, port={port}, dbname={dbname}, user={user}")

                # Verify all required values are present
                if not all([dbname, user, password, host, port]):
                    missing = [k for k, v in {
                        "postgres-db": dbname,
                        "postgres-user": user,
                        "postgres-password": password,
                        "postgres-service": host,
                        "postgres-port": port
                    }.items() if not v]
                    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
                
                self._pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=host,
                    port=port
                )
                if self._pool:
                    logger.info("Connection pool created successfully")
                    self._create_table()
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(f"Error while connecting to PostgreSQL: {error}")
                raise

    def _create_table(self):
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
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_time FLOAT
                )
                """)
                conn.commit()
                cursor.close()
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(f"Error creating table: {error}")
            finally:
                self._pool.putconn(conn)

    def get_connection(self):
        return self._pool.getconn()

    def return_connection(self, conn):
        if conn:
            self._pool.putconn(conn) 
