import sys
import time
import subprocess
import signal
import os
import shutil

# Check for watchfiles
try:
    from watchfiles import watch
except ImportError:
    print("Error: 'watchfiles' is not installed. Please install it via pip.")
    sys.exit(1)

PORT = 8080
PROCESS = None

def free_port(port):
    """
    Check if port is free, otherwise free it using fuser and wait.
    """
    import socket
    
    # helper to check if port is open
    def is_port_in_use(p):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', p)) == 0

    if not is_port_in_use(port):
        return

    print(f"Port {port} is in use. Attempting to free...")
    
    if shutil.which("fuser"):
        # Try to kill process on port
        subprocess.run(["fuser", "-k", f"{port}/tcp"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        # Wait and retry check
        for i in range(10):
            if not is_port_in_use(port):
                print(f"Port {port} successfully freed.")
                return
            time.sleep(0.5)
            
        print(f"Warning: Could not free port {port} after multiple attempts.")
    else:
        print("Warning: 'fuser' command not found. Cannot automatically free port.")

def stop_server():
    """
    Stop the running server process and ensure port is freed.
    """
    global PROCESS
    if PROCESS:
        print("Stopping application...")
        if PROCESS.poll() is None:
            PROCESS.terminate()
            try:
                PROCESS.wait(timeout=2)
            except subprocess.TimeoutExpired:
                print("Process did not terminate gracefully, killing...")
                PROCESS.kill()
        PROCESS = None
    
    # Double check port is free
    free_port(PORT)

def start_server():
    """
    Start the application server.
    """
    global PROCESS
    stop_server()
    print("Starting application...")
    # Use the same python executable that is running this script
    PROCESS = subprocess.Popen([sys.executable, 'test/test.py'])

def signal_handler(signum, frame):
    """
    Handle interrupt signals to cleanly exit.
    """
    print("\nInterrupt received. Exiting...")
    stop_server()
    sys.exit(0)

def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"Initializing NiceTheme Runner on port {PORT}...")
    
    # Watch directories
    watch_paths = ['./nicetheme', './test']
    valid_paths = [p for p in watch_paths if os.path.exists(p)]
    
    if not valid_paths:
        print("Error: No paths to watch found.")
        return

    # Initial Start
    start_server()

    # Watch loop
    try:
        print(f"Watching for changes in: {', '.join(valid_paths)}")
        for changes in watch(*valid_paths):
            change_list = list(changes)
            print(f"\nDetected {len(change_list)} change(s). Restarting...")
            start_server()
    except Exception as e:
        print(f"Error in watcher loop: {e}")
        stop_server()

if __name__ == '__main__':
    main()
