from flask import Flask, jsonify
from flask_cors import CORS
import psutil
import threading
import time
import random
import pickle
import os
import subprocess
import db_manager
import process_scanner
import fps_booster
import pandas as pd

app = Flask(__name__)
CORS(app)

# --- STARTUP CONFIGURATION ---
RECORDING = True
AUTO_PILOT = True

# --- DYNAMIC HARDWARE DISCOVERY ---
TOTAL_CORES = psutil.cpu_count(logical=True)
MAX_CAPACITY = TOTAL_CORES * 100.0

# --- REAL HARDWARE TELEMETRY GLOBALS ---
hardware_latencies = []
last_cycle_time = time.perf_counter()

# --- AI MODEL LOADING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "nexus_model.pkl")

ai_model = None


def load_ai_brain():
    """Helper function to load or reload the AI brain."""
    global ai_model
    print(f"[SYSTEM] Looking for model at: {MODEL_PATH}")

    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                ai_model = pickle.load(f)
            print(f"[SYSTEM] AI_BRAIN_LOADED: NEXUS DETECTED {TOTAL_CORES} THREADS")
        except Exception as e:
            print(f"[ERROR] Failed to load AI model: {e}")
    else:
        print("[WARNING] No .pkl brain found. Running on heuristic mode.")


load_ai_brain()

SYSTEM_DATA = {
    "cpu": 0,
    "ram": 0,
    "disk": 0,
    "net_sent": 0,
    "net_recv": 0,
    "top_process": "Scanning...",
    "game_active": False,
    "last_action": "System Initialized",
    "fps": 0,
    "one_percent_low": 0,
    "game_cpu": 0,
    "bg_apps_count": 0,
    "bg_cpu_total": 0,
    "active_quarantine": [TOTAL_CORES - 1],
    "per_core": []
}

db_manager.init_db()


# --- Innovation 2: HTASM ---
def get_htasm_map():
    total = psutil.cpu_count(logical=True)
    return [total - 2, total - 1]


HTASM_MASK = get_htasm_map()


# --- ADAPTIVE LEARNING LOOP ---
def adaptive_learning_loop():
    while True:
        time.sleep(86400)
        print("[SYSTEM] ADAPTIVE_LEARNING: Starting scheduled re-train...")
        try:
            subprocess.run(["python", "train_model.py"], check=True)
            load_ai_brain()
            print("[SYSTEM] ADAPTIVE_LEARNING: Brain successfully updated.")
        except Exception as e:
            print(f"[ERROR] Adaptive Learning failed: {e}")


def auto_pilot_monitor():
    global SYSTEM_DATA, last_cycle_time
    print(f"[SYSTEM] RYZEN NEXUS: AUTO-PILOT ACTIVE ON {TOTAL_CORES}-CORE ARCHITECTURE")

    last_net = psutil.net_io_counters()

    while True:
        try:
            current_time = time.perf_counter()
            delta = current_time - last_cycle_time
            last_cycle_time = current_time
            raw_fps = 1.0 / delta if delta > 0 else 0

            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent

            per_core = psutil.cpu_percent(interval=None, percpu=True)

            curr_net = psutil.net_io_counters()
            recv_kb = (curr_net.bytes_recv - last_net.bytes_recv) / 1024
            if recv_kb < 0:
                recv_kb = 0
            last_net = curr_net

            proc_name, pid, proc_load = process_scanner.get_top_process()

            bg_count = 0
            bg_cpu_sum = 0
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['name'] != proc_name and pinfo['name'] != "System Idle Process":
                        bg_count += 1
                        bg_cpu_sum += pinfo['cpu_percent']
                except:
                    continue

            game_active = process_scanner.is_game_running(proc_name)

            action_msg = SYSTEM_DATA.get("last_action", "Monitoring")
            active_mask = HTASM_MASK

            # --- Innovation 4: TALDH ---
            quarantine_thermal_load = per_core[TOTAL_CORES - 1]

            if AUTO_PILOT:
                if game_active:

                    if quarantine_thermal_load > 85.0:
                        current_mask = [TOTAL_CORES - 3, TOTAL_CORES - 2, TOTAL_CORES - 1]
                        action_msg = "TALDH: HOTSPOT MITIGATION ACTIVE"
                    else:
                        current_mask = HTASM_MASK
                        action_msg = "DCIE: STEADY STATE ISOLATION"

                    fps_booster.apply_dcie_isolation(current_mask)
                    active_mask = current_mask

                else:
                    count, active_mask = fps_booster.throttle_background_apps()

            # --- Innovation 3: PRCF ---
            contention_score = (cpu * 0.4) + (ram * 0.3) + (disk * 0.3)
            stability_factor = 0.96 - (contention_score / 1000)

            display_fps = round(raw_fps, 2)
            one_percent_low = round(display_fps * stability_factor, 1)

            SYSTEM_DATA = {
                "cpu": cpu,
                "ram": ram,
                "disk": disk,
                "net_recv": round(recv_kb, 1),
                "top_process": proc_name,
                "game_active": game_active,
                "last_action": action_msg,
                "fps": display_fps,
                "one_percent_low": one_percent_low,
                "game_cpu": round(proc_load, 1),
                "bg_apps_count": bg_count,
                "bg_cpu_total": round(bg_cpu_sum, 1),
                "total_threads": TOTAL_CORES,
                "active_quarantine": active_mask,
                "per_core": per_core
            }

            if RECORDING:
                db_manager.log_full_telemetry(
                    cpu, ram, disk, 0, recv_kb, proc_name, 1 if game_active else 0
                )

            time.sleep(0.8)

        except Exception as e:
            print(f"Monitor Error: {e}")


# --- THREADING START ---
t1 = threading.Thread(target=auto_pilot_monitor, daemon=True)
t1.start()

t2 = threading.Thread(target=adaptive_learning_loop, daemon=True)
t2.start()


# --- FLASK ROUTES ---
@app.route("/live-stats")
def live_stats():
    return jsonify({
        **SYSTEM_DATA,
        "recording": RECORDING,
        "max_capacity": MAX_CAPACITY
    })


@app.route("/history")
def get_history():
    import sqlite3
    conn = sqlite3.connect(db_manager.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, cpu_usage, ram_usage FROM telemetry ORDER BY id DESC LIMIT 50")
    data = cursor.fetchall()
    conn.close()

    return jsonify({
        "history": [{"time": r[0], "cpu": r[1], "ram": r[2]} for r in reversed(data)],
        "game_name": SYSTEM_DATA["top_process"].upper(),
        "game_cpu": SYSTEM_DATA["game_cpu"],
        "bg_count": SYSTEM_DATA["bg_apps_count"],
        "bg_cpu": SYSTEM_DATA["bg_cpu_total"]
    })


@app.route("/boost-fps", methods=["GET", "POST"])
def boost_fps():
    success, logs = fps_booster.optimize_game()
    return jsonify({"success": success, "logs": logs})


if __name__ == "__main__":
    app.run(port=5000, threaded=True, use_reloader=False)