import sqlite3
import os
import time

def init_db():
    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)
    
    db_path = 'data/database.db'
    print(f"Initializing database at {db_path}")
    
    # Try to connect to the database, with retries
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Connect to SQLite database (creates file if it doesn't exist)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create items table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            ''')
            
            # Check if table is empty
            cursor.execute('SELECT COUNT(*) FROM items')
            count = cursor.fetchone()[0]
            
            # Insert sample data only if table is empty
            if count == 0:
                sample_data = [
                    ('1', 'Sample item 1', '2023-01-01T12:00:00'),
                    ('2', 'Sample item 2', '2023-01-02T12:00:00'),
                    ('3', 'Sample item 3', '2023-01-03T12:00:00')
                ]
                
                cursor.executemany(
                    'INSERT INTO items (id, content, created_at) VALUES (?, ?, ?)',
                    sample_data
                )
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            print(f"Database initialized successfully at {db_path}")
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in 2 seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(2)
            else:
                print("Failed to initialize database after multiple attempts")
                return False

if __name__ == "__main__":
    init_db()
