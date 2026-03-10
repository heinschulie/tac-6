"""
Tests for CSV export endpoints
"""

import pytest
import csv
import io
import sqlite3
import tempfile
import os
from unittest.mock import patch
from fastapi.testclient import TestClient


@pytest.fixture
def test_db():
    """Create a test database with sample data"""
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_file.close()

    conn = sqlite3.connect(db_file.name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    ''')

    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                   ('Alice', 'alice@example.com'))
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                   ('Bob', 'bob@example.com'))

    cursor.execute('''
        CREATE TABLE empty_table (
            id INTEGER PRIMARY KEY,
            value TEXT
        )
    ''')

    conn.commit()
    conn.close()

    yield db_file.name

    os.unlink(db_file.name)


@pytest.fixture
def client(test_db):
    """Create test client with patched database path"""
    _real_connect = sqlite3.connect

    def patched_connect(db_path, *args, **kwargs):
        if db_path == "db/database.db":
            return _real_connect(test_db, *args, **kwargs)
        return _real_connect(db_path, *args, **kwargs)

    with patch('core.sql_processor.sqlite3.connect', side_effect=patched_connect), \
         patch('server.sqlite3.connect', side_effect=patched_connect):

        from server import app
        with TestClient(app) as c:
            yield c


class TestTableExport:
    """Test GET /api/table/{table_name}/export"""

    def test_export_valid_table(self, client):
        """Valid table returns CSV with correct headers and data"""
        response = client.get("/api/table/users/export")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        assert 'filename="users.csv"' in response.headers["content-disposition"]

        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)
        assert rows[0] == ["id", "name", "email"]
        assert len(rows) == 3  # header + 2 data rows
        assert rows[1][1] == "Alice"
        assert rows[2][1] == "Bob"

    def test_export_empty_table(self, client):
        """Empty table returns CSV with headers only"""
        response = client.get("/api/table/empty_table/export")
        assert response.status_code == 200

        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)
        assert rows[0] == ["id", "value"]
        assert len(rows) == 1  # header only

    def test_export_nonexistent_table(self, client):
        """Nonexistent table returns 404"""
        response = client.get("/api/table/nonexistent/export")
        assert response.status_code == 404

    def test_export_invalid_table_name(self, client):
        """SQL injection attempt returns 400"""
        response = client.get("/api/table/users'; DROP TABLE users; --/export")
        assert response.status_code in (400, 422)


class TestResultsExport:
    """Test POST /api/export-results"""

    def test_export_valid_results(self, client):
        """Valid columns/results returns correct CSV"""
        payload = {
            "columns": ["name", "age"],
            "results": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ]
        }
        response = client.post("/api/export-results", json=payload)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        assert 'filename="query_results.csv"' in response.headers["content-disposition"]

        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)
        assert rows[0] == ["name", "age"]
        assert rows[1] == ["Alice", "30"]
        assert rows[2] == ["Bob", "25"]

    def test_export_empty_results(self, client):
        """Empty results returns CSV with headers only"""
        payload = {
            "columns": ["name", "age"],
            "results": []
        }
        response = client.post("/api/export-results", json=payload)
        assert response.status_code == 200

        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)
        assert rows[0] == ["name", "age"]
        assert len(rows) == 1

    def test_export_results_missing_keys(self, client):
        """Results with missing keys produce empty cells"""
        payload = {
            "columns": ["name", "age", "email"],
            "results": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "email": "bob@test.com"}
            ]
        }
        response = client.post("/api/export-results", json=payload)
        assert response.status_code == 200

        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)
        assert rows[1] == ["Alice", "30", ""]
        assert rows[2] == ["Bob", "", "bob@test.com"]
