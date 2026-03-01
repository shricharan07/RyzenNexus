import psutil
import os

# Detect total threads dynamically for any system (12 for your Ryzen 6600H)
TOTAL_THREADS = psutil.cpu_count(logical=True)

# 1. The "Victims"
BACKGROUND_HOGS = ["chrome.exe", "discord.exe", "spotify.exe", "teams.exe", "edge.exe", "browser.exe"]

# 2. The "VIPs"
GAMES = ["valorant.exe", "csgo.exe", "dota2.exe", "minecraft.exe", "gta5.exe", "code.exe", "eldenring.exe"]

def set_high_priority_and_affinity(pid, is_game=True):
    try:
        p = psutil.Process(pid)
        
        if is_game:
            # Set to HIGH PRIORITY
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            
            # PIN TO PERFORMANCE CORES (Use all cores EXCEPT the last two)
            # This ensures the game has a massive clear highway.
            performance_cores = list(range(0, TOTAL_THREADS - 2))
            p.cpu_affinity(performance_cores)
            return True, f"SET_TO_HIGH_CORES: {performance_cores}"
        else:
            # Set to IDLE PRIORITY (Lowest)
            p.nice(psutil.IDLE_PRIORITY_CLASS)
            
            # PIN TO THE VERY LAST LOGICAL THREAD (e.g., Core 11)
            # We use the highest index to keep them far from Core 0.
            efficiency_core = [TOTAL_THREADS - 1]
            p.cpu_affinity(efficiency_core)
            return True, f"SET_TO_LOW_CORE: {efficiency_core}"
    except Exception as e:
        return False, str(e)

def throttle_background_apps(game_pid=None):
    throttled_count = 0
    # Capture every process running on Windows
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            
            # CORE LOGIC: If it's NOT the game and NOT a critical system process, isolate it
            if pid != game_pid and name != "System Idle Process" and pid != os.getpid():
                # Set to IDLE priority and move to the last logical thread (Core 11)
                p = psutil.Process(pid)
                p.nice(psutil.IDLE_PRIORITY_CLASS)
                p.cpu_affinity([TOTAL_THREADS - 1]) 
                throttled_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return throttled_count

def optimize_game():
    game_found = None
    game_name = "Unknown"
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() in GAMES:
                game_found = proc
                game_name = proc.info['name']
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    log = []
    if game_found:
        pid = game_found.info['pid']
        
        # 1. Boost the Game
        success, msg = set_high_priority_and_affinity(pid, is_game=True)
        if success:
            log.append(f"CORE_REMAP: '{game_name}' moved to Cores 0-{TOTAL_THREADS-3}.")
            log.append(f"PRIORITY_BOOST: '{game_name}' set to HIGH.")
        else:
            log.append(f"ACCESS_DENIED: Run as Administrator to unlock core pinning.")
        
        # 2. Quarantine Background Apps
        count = throttle_background_apps()
        if count > 0:
            log.append(f"QUARANTINE: {count} apps pushed to Core {TOTAL_THREADS-1}.")
            
        return True, log
    else:
        return False, ["WAITING_FOR_TARGET: Engage AI Core Pinning by launching a game."]