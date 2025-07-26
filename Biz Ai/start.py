import subprocess
import sys
import time
import os

def start_services():
    try:
        fastapi = subprocess.Popen(
            ["uvicorn", "main:app", "--reload"],
            cwd="backend"
        )
        
        frontend = subprocess.Popen(
            ["npm", "run", "electron:dev"],
            shell=True if os.name == 'nt' else False
        )
        
        workflow = subprocess.Popen(
            [sys.executable, "workflow_manager.py"],
            cwd="backend"
        )
        
        print("All services started. Press Ctrl+C to stop all services.")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down services...")
        for process in [fastapi, frontend, workflow]:
            if process:
                process.terminate()
                process.wait()
        print("All services stopped.")

if __name__ == "__main__":
    start_services() 