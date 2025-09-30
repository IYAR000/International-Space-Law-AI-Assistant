"""
Database connection and configuration for International Space Law AI Assistant
"""
import os
from typing import Optional
import sqlite3
import psycopg2
import pymysql
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'sqlite')  # sqlite, postgresql, mysql
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.name = os.getenv('DB_NAME', 'space_law_db')
        self.user = os.getenv('DB_USER', '')
        self.password = os.getenv('DB_PASSWORD', '')
        self.sqlite_path = os.getenv('SQLITE_PATH', 'space_law.db')
    
    def get_connection_string(self) -> str:
        """Get database connection string based on type"""
        if self.db_type == 'sqlite':
            return f"sqlite:///{self.sqlite_path}"
        elif self.db_type == 'postgresql':
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        elif self.db_type == 'mysql':
            return f"mysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup"""
        connection = None
        try:
            if self.config.db_type == 'sqlite':
                connection = sqlite3.connect(self.config.sqlite_path)
                connection.row_factory = sqlite3.Row
            elif self.config.db_type == 'postgresql':
                connection = psycopg2.connect(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.name,
                    user=self.config.user,
                    password=self.config.password
                )
            elif self.config.db_type == 'mysql':
                connection = pymysql.connect(
                    host=self.config.host,
                    port=int(self.config.port),
                    database=self.config.name,
                    user=self.config.user,
                    password=self.config.password,
                    charset='utf8mb4'
                )
            else:
                raise ValueError(f"Unsupported database type: {self.config.db_type}")
            
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def initialize_database(self):
        """Initialize database with schema"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Read and execute schema
                with open('database/schema.sql', 'r') as f:
                    schema_sql = f.read()
                
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
                for statement in statements:
                    cursor.execute(statement)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global database configuration
db_config = DatabaseConfig()
db_manager = DatabaseManager(db_config)
