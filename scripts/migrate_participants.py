import sqlite3
import os

db_path = os.path.join('instance', 'agency.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Create viaggio_partecipanti table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS viaggio_partecipanti (
                viaggio_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                PRIMARY KEY (viaggio_id, cliente_id),
                FOREIGN KEY (viaggio_id) REFERENCES viaggi (id),
                FOREIGN KEY (cliente_id) REFERENCES clienti (id)
            )
        """)
        conn.commit()
        print("Table 'viaggio_partecipanti' created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print(f"Database {db_path} not found.")
