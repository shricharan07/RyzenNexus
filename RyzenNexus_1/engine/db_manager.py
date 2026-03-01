import sqlite3
import time
import os

# We store the DB in a 'database' folder
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/nexus_real_data.db')

def init_db():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Creating a RICH table for deep learning later
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                cpu_usage REAL,
                ram_usage REAL,
                disk_usage REAL,
                network_sent REAL,
                network_recv REAL,
                top_process TEXT,
                is_game_active INTEGER
            )
        ''')
        conn.commit()
        conn.close()
        print("[DB] REAL DATA ENGINE: INITIALIZED")
    except Exception as e:
        print(f"[ERROR] Database Error: {e}")

def log_full_telemetry(cpu, ram, disk, net_sent, net_recv, process, is_game):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO telemetry 
            (timestamp, cpu_usage, ram_usage, disk_usage, network_sent, network_recv, top_process, is_game_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (time.time(), cpu, ram, disk, net_sent, net_recv, process, is_game))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging Failed: {e}")

if __name__ == "__main__":
    init_db()