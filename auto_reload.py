import os
import sys
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script_path):
        self.script_path = script_path
        self.process = None
        self.restart_app()
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.py'):
            print(f"File {event.src_path} was modified. Restarting app...")
            self.restart_app()
    
    def restart_app(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        
        self.process = subprocess.Popen([sys.executable, self.script_path])
    
    def stop(self):
        if self.process:
            self.process.terminate()

def main():
    script_path = "medimate.py"  # Your main script
    
    if not os.path.exists(script_path):
        print(f"Script {script_path} not found!")
        return
    
    event_handler = ChangeHandler(script_path)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    
    print(f"Watching for changes in {script_path}...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        event_handler.stop()
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()