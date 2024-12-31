import sqlite3

class DatabaseManager:
    def __init__(self, db_path='wtk_data.db', timeout=5):
        """
        Initializes the DatabaseManager with the given database path/name and timeout.
        """
        self.conn = sqlite3.connect(db_path, timeout=timeout)
        self.create_table()

    def create_table(self):
        """
        Creates the cached_data table if it does not already exist.
        """
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS cached_data (
                    key TEXT PRIMARY KEY,
                    data TEXT
                ''')

    def get_data(self, key: str) -> str:
        """
        Retrieves data from the database associated with the given key.

        Returns:
            str: The data associated with the key, or None if the key does not exist.
        """
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT data FROM cached_data WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row[0] if row else None

    def store_data(self, key: str, data):
        """
        Stores data in the database with the given key.

        Args:
            key (str): The key associated with the data.
            data (str): The data to be stored.
        """
        
        with self.conn:
            self.conn.execute('INSERT OR REPLACE INTO cached_data (key, data) VALUES (?, ?)', (key, data))