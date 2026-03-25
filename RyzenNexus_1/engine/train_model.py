import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../database/nexus_real_data.db')
MODEL_PATH = os.path.join(os.path.dirname(__file__), "nexus_model.pkl")

def train_nexus_ai():
    # 1. Load data from your real sessions
    if not os.path.exists(DB_PATH):
        print("ERROR: Database file not found at " + DB_PATH)
        return

    conn = sqlite3.connect(DB_PATH)
    try:
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

    # ✅ ADD THIS LINE
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    # 4. Save the Model
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f, protocol=4)
        
    print("SUCCESS: AI Model trained and saved to " + MODEL_PATH)

if __name__ == "__main__":
    train_nexus_ai()