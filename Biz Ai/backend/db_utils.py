import sqlite3
from pathlib import Path
import logging

class DatabaseManager:
    def __init__(self):
        self.db_path = Path('rfq_data.db')
        self.logger = logging.getLogger(__name__)
        self.initialize_db()

    def initialize_db(self):
        """Create the database and tables if they don't exist."""
        try:
            # Ensure the database file exists before connecting
            self.db_path.parent.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS rfq_cases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_rfq TEXT UNIQUE NOT NULL,
                        our_rfq TEXT UNIQUE DEFAULT NULL,
                        supplier_quote TEXT UNIQUE DEFAULT NULL
                    )
                ''')
                # Create indexes for faster lookups
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_client_rfq ON rfq_cases(client_rfq)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_our_rfq ON rfq_cases(our_rfq)')
                conn.commit()
        except Exception as e:
            self.logger.error(f"Database initialization error: {str(e)}")
            raise

    def insert_rfq_case(self, client_rfq, our_rfq=None):
        """Insert a new RFQ case."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO rfq_cases (client_rfq, our_rfq)
                    VALUES (?, ?)
                ''', (client_rfq, our_rfq))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # If the record already exists, just update it
            cursor.execute('''
                UPDATE rfq_cases 
                SET our_rfq = ?
                WHERE client_rfq = ?
            ''', (our_rfq, client_rfq))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Error inserting RFQ case: {str(e)}")
            raise

    def update_supplier_quote(self, client_rfq, supplier_quote):
        """Update supplier quote number for an existing RFQ case."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE rfq_cases 
                    SET supplier_quote = ?
                    WHERE client_rfq = ?
                ''', (supplier_quote, client_rfq))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error updating supplier quote: {str(e)}")
            raise

    def get_case_by_our_rfq(self, our_rfq):
        """Get case details using our RFQ number."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT client_rfq, supplier_quote
                    FROM rfq_cases
                    WHERE our_rfq = ?
                ''', (our_rfq,))
                return cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Error fetching case by our RFQ: {str(e)}")
            raise

    def get_case_by_client_rfq(self, client_rfq):
        """Get case details using client RFQ number."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT our_rfq, supplier_quote
                    FROM rfq_cases
                    WHERE client_rfq = ?
                ''', (client_rfq,))
                return cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Error fetching case by client RFQ: {str(e)}")
            raise

    def update_our_rfq(self, client_rfq, our_rfq):
        """Update our RFQ number for an existing case."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE rfq_cases 
                    SET our_rfq = ?
                    WHERE client_rfq = ?
                ''', (our_rfq, client_rfq))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error updating our RFQ: {str(e)}")
            raise

    def reset_database(self):
        """Reset the database by dropping and recreating the table."""
        try:
            if self.db_path.exists():
                self.db_path.unlink()  # Delete the database file
            self.initialize_db()  # Recreate the database
            return True
        except Exception as e:
            self.logger.error(f"Error resetting database: {str(e)}")
            return False 