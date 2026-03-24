import psutil
import os

# --- DYNAMIC HARDWARE DETECTION ---
TOTAL_THREADS = psutil.cpu_count(logical=True)
SAFE_THRESHOLD = 80.0  # AI Overflow Trigger

# 1. The "Victims"
BACKGROUND_HOGS = ["chrome.exe", "discord.exe", "spotify.exe", "teams.exe", "edge.exe", "browser.exe"]

# 2. The "VIPs"
GAMES = ["valorant.exe", "csgo.exe", "dota2.exe", "minecraft.exe", "gta5.exe", "code.exe", "eldenring.exe"]

# NEW: Dynamic Pool for Overflow (Last 4 threads: 11, 10, 9, 8)
QUARANTINE_POOL = list(range(TOTAL_THREADS - 1, TOTAL_THREADS - 5, -1))

def get_active_quarantine_mask():
    """AI Load Monitor: Expands the mask if usage hits 80%"""
    per_core_usage = psutil.cpu_percent(interval=None, percpu=True)
    active_mask = []
    
    for core_idx in QUARANTINE_POOL:
        active_mask.append(core_idx)
        # If the current core is breathing easy (<80%), we don't need the next one
        if per_core_usage[core_idx] < SAFE_THRESHOLD:
            break
    return active_mask

def set_high_priority_and_affinity(pid, is_game=True):
    try:
        p = psutil.Process(pid)
        if is_game:
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            # Reserve Cores 0-7 for Game
            performance_cores = list(range(0, TOTAL_THREADS - 4))
            p.cpu_affinity(performance_cores)
            return True, f"GAME_BOOST: {performance_cores}"
        else:
            p.nice(psutil.IDLE_PRIORITY_CLASS)
            # Use Dynamic Overflow Mask
            target_mask = get_active_quarantine_mask()
            p.cpu_affinity(target_mask)
            return True, f"BG_ISOLATED: {target_mask}"
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False, "Access Denied"

def throttle_background_apps():
    throttled_count = 0
    current_mask = get_active_quarantine_mask() # AI decides mask size here
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() in BACKGROUND_HOGS:
                # Reuse our dynamic affinity logic
                success, msg = set_high_priority_and_affinity(proc.info['pid'], is_game=False)
                if success: throttled_count += 1
        except: continue
    return throttled_count, current_mask

def optimize_game():
    game_found = None
    game_name = "Unknown"
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() in GAMES:
                game_found = proc
                game_name = proc.info['name']
                break
        except: continue

    log = []
    if game_found:
        pid = game_found.info['pid']
        set_high_priority_and_affinity(pid, is_game=True)
        
        # New: Capture the count AND the active mask for the terminal log
        count, active_cores = throttle_background_apps()
        
        log.append(f"STABILITY_MODE: 80% HEADROOM GUARD ACTIVE")
        log.append(f"CLEANUP: {count} apps on Cores {active_cores}")
        return True, log
    else:
        return False, ["WAITING_FOR_TARGET: Launch a game to engage AI."]