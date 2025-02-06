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
        if self.process and self.process.poll() is None: #Check if the process is running
            print(f"Stopping process with PID: {self.process.pid}", flush=True)
            try:
                self.process.terminate() #Try graceful termination first
                self.process.wait(timeout=10)  # Wait for it to finish
                print("Process stopped gracefully.", flush=True)

            except subprocess.TimeoutExpired:
                print("Process did not terminate gracefully. Using SIGKILL.", flush=True)
                try:
                    self.process.kill()  # Forcefully kill the process
                    self.process.wait(timeout=5) #Wait for kill to happen
                    print("Process killed.", flush=True)
                except Exception as e:
                    print(f"Error killing process: {e}", flush=True)
            except Exception as e:
                print(f"Error stopping process: {e}", flush=True)
            finally:
                self.process = None  # Reset process after it's finished

    def _kill_ffmpeg_children(self):
        pass

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
