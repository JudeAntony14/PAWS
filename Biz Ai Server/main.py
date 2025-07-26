import subprocess
import time
import sys
import os
import signal

def run_scripts():
    print("\nStarting Email Testing and Extraction System...")
    
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    tester_process = None
    extractor_process = None
    
    try:

        print("\nStarting Email Tester...")
        tester_process = subprocess.Popen([sys.executable, os.path.join(current_dir, 'Tester.py')],
                                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
        
        
        print("\nStarting Email Extractor...")
        time.sleep(5)
        
        
        print("\nStarting Email Extractor...")
        extractor_process = subprocess.Popen([sys.executable, os.path.join(current_dir, 'EmailExtractor.py')],
                                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
        
        while True:
           
            if tester_process.poll() is not None or extractor_process.poll() is not None:
                raise Exception("One of the processes terminated unexpectedly")
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\nShutting down all processes...")
        if tester_process:
            if os.name == 'nt':  
                tester_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:  # Unix/Linux
                tester_process.send_signal(signal.SIGINT)
            tester_process.wait(timeout=5)  
            
        if extractor_process:
            if os.name == 'nt':  
                extractor_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:  
                extractor_process.send_signal(signal.SIGINT)
            extractor_process.wait(timeout=5)  
            
        if tester_process and tester_process.poll() is None:
            tester_process.terminate()
        if extractor_process and extractor_process.poll() is None:
            extractor_process.terminate()
            
        print("All processes terminated.")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        if tester_process and tester_process.poll() is None:
            tester_process.terminate()
        if extractor_process and extractor_process.poll() is None:
            extractor_process.terminate()
    
    finally:
        if tester_process and tester_process.poll() is None:
            tester_process.kill()
        if extractor_process and extractor_process.poll() is None:
            extractor_process.kill()

if __name__ == "__main__":
    run_scripts() 