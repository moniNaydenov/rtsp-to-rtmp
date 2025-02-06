import subprocess
import time
import os
import signal
import threading
from dotenv import load_dotenv
import psutil  # Import psutil
from datetime import datetime


class BackgroundProcessManager:
    def __init__(self, command_template):
        self.command_template = command_template
        self.process = None
        self.timer = None
        load_dotenv()
        self.input_stream = os.environ.get("ENV_INPUT_STREAM")
        self.output_stream = os.environ.get("ENV_OUTPUT_STREAM")     
    def _run_command(self):
        """Runs the command in the background."""
        command = self.command_template % {
            'ENV_INPUT_STREAM': self.input_stream,
            'ENV_OUTPUT_STREAM': self.output_stream
        }
        print(f"Running command: {command}")
        try:
            self.process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
            print(f"Process started with PID: {self.process.pid}", flush=True)
        except Exception as e:
            print(f"Error starting process: {e}", flush=True)

    def _stop_command(self):
        if self.process:
            print(f"Stopping process with PID: {self.process.pid}")
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM) #Try to kill the group first
                self.process.wait(timeout=15)  # Give it time to exit gracefully
                print("Process stopped successfully.", flush=True)

            except subprocess.TimeoutExpired:
                print("Process did not terminate gracefully, killing it.", flush=True)
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except ProcessLookupError: #Handle the case when group is already killed.
                print("Process group already killed.", flush=True)
            except Exception as e:
                print(f"Error stopping process: {e}", flush=True)
            finally:
                self.process = None #Reset the process
        self._kill_ffmpeg_children() #Kill the remaining children

    def _kill_ffmpeg_children(self):
        if self.process and self.process.pid:
            try:
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)  # Get all child processes recursively
                for child in children:
                    print(f"Killing child process: {child.pid}", flush=True)
                    child.kill() #Kill directly
            except psutil.NoSuchProcess:
               print("Parent process is not running.", flush=True)
            except Exception as e:
                print(f"Error killing child processes: {e}", flush=True)

    def _restart_command(self):
        """Stops and restarts the command."""
        print("Restarting command...", flush=True)
        self._stop_command()
        self._run_command()
        # Reschedule the timer
        self.timer = threading.Timer(900, self._restart_command)  # 900 seconds = 15 minutes
        self.timer.start()

    def start(self):
        """Starts the command and schedules restarts."""
        self._run_command()
        self.timer = threading.Timer(900, self._restart_command)
        self.timer.start()
        now = datetime.now()
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Starting again - {formatted_datetime}", flush=True)



    def stop(self):
        """Stops the command and cancels the restart timer."""
        self._stop_command()
        if self.timer:
            self.timer.cancel()
        print("Background process manager stopped.", flush=True)


if __name__ == "__main__":
    # Example usage:
    command_template = "ffmpeg -rtsp_transport tcp -i %(ENV_INPUT_STREAM)s -f flv -c:v copy -c:a copy %(ENV_OUTPUT_STREAM)s"

    manager = BackgroundProcessManager(command_template)
    manager.start()

    try:
        # Keep the main thread alive to allow the background thread to run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping...", flush=True)
        manager.stop()
