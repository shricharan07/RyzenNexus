import psutil

# Add any app you want to detect as a "Game" here
GAME_SIGNATURES = [
    "valorant.exe", "csgo.exe", "dota2.exe", 
    "cyberpunk2077.exe", "gta5.exe", "minecraft.exe",
    "chrome.exe", "code.exe" # Added 'code.exe' so you can test it right now!
]

def get_top_process():
    """
    Finds the process using the most CPU right now.
    """
    highest_cpu = 0
    top_proc_name = "System"
    top_proc_pid = None

    try:
        # Scan all running processes
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                p_cpu = proc.info['cpu_percent']
                # Filter out idle process
                if p_cpu > highest_cpu and proc.info['name'] != "System Idle Process":
                    highest_cpu = p_cpu
                    top_proc_name = proc.info['name']
                    top_proc_pid = proc.info['pid']
            except:
                pass
    except:
        pass
        
    return top_proc_name, top_proc_pid, highest_cpu

def is_game_running(process_name):
    if not process_name: return False
    return process_name.lower() in GAME_SIGNATURES