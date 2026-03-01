import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle # Changed from joblib for better server compatibility
import os

# Updated to use absolute path to ensure the file is created in the correct folder
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/nexus_real_data.db')
MODEL_PATH = r'D:\RyzenNexus_1 (2)\RyzenNexus_1\engine\nexus_model.pkl'

def train_nexus_ai():
    # 1. Load data from your real sessions
    if not os.path.exists(DB_PATH):
        print("ERROR: Database file not found at " + DB_PATH)
        return

    conn = sqlite3.connect(DB_PATH)
    # Using the columns that match your existing db_manager schema
    try:
        # UPDATED: Added 'ORDER BY id DESC LIMIT 5000' to focus on your latest gaming patterns
        query = "SELECT cpu_usage, ram_usage, network_recv, is_game_active FROM telemetry ORDER BY id DESC LIMIT 5000"
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        print("ERROR: Could not read telemetry table. " + str(e))
        return
    finally:
        conn.close()

    if len(df) < 10:
        print("ERROR: Not enough data yet. Use your PC for a few more minutes!")
        return

    # 2. Prepare Features (Input) and Labels (Output)
    X = df[['cpu_usage', 'ram_usage', 'network_recv']]
    y = df['is_game_active']

    # 3. Train the "Brain"
    print("Training Ryzen Nexus AI...")
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    # 4. Save the Model using pickle protocol 4 for maximum compatibility
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f, protocol=4)
        
    print("SUCCESS: AI Model trained and saved to " + MODEL_PATH)

if __name__ == "__main__":
    train_nexus_ai()