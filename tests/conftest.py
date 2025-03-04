import pytest
from unittest.mock import MagicMock, patch
import psycopg2
from psycopg2.pool import SimpleConnectionPool

@pytest.fixture(autouse=True)
def mock_db_connection():
    """Mock database connection for all tests"""
    with patch('psycopg2.pool.SimpleConnectionPool') as mock_pool:
        # Create a mock connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Configure pool mock
        mock_pool.return_value = MagicMock(spec=SimpleConnectionPool)
        mock_pool.return_value.getconn.return_value = mock_conn
        
        yield mock_pool

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set test environment variables"""
    monkeypatch.setenv('TESTING', 'true') 