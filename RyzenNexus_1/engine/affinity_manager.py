import psutil

def get_cpu_layout():
    # Detect total logical cores
    return list(range(psutil.cpu_count()))

def pin_to_performance_cores(pid):
    """
    Pins the Game to the first 4 cores (Performance Cores).
    """
    try:
        p = psutil.Process(pid)
        # We give the game the first 4 logical cores
        p.cpu_affinity([0, 1, 2, 3])
        return True
    except Exception as e:
        print(f"Pinning Error: {e}")
        return False

def throttle_to_efficiency_cores():
    """
    Finds background hogs and moves them to the LAST cores.
    """
    all_cores = get_cpu_layout()
    # Use cores from index 4 onwards for background stuff
    efficiency_cores = all_cores[4:] if len(all_cores) > 4 else [all_cores[-1]]
    
    BACKGROUND_NAMES = ["chrome.exe", "discord.exe", "spotify.exe"]
    
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() in BACKGROUND_NAMES:
            try:
                p = psutil.Process(proc.info['pid'])
                p.cpu_affinity(efficiency_cores)
            except:
                pass