import subprocess
import time
import os
import signal
import threading
from dotenv import load_dotenv  # Import load_dotenv


class BackgroundProcessManager:
    def __init__(self, command_template, input_stream, output_stream):
        self.command_template = command_template
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.process = None
        self.timer = None

    def _run_command(self):
        """Runs the command in the background."""
        command = self.command_template % {
            'ENV_INPUT_STREAM': self.input_stream,
            'ENV_OUTPUT_STREAM': self.output_stream
        }
        print(f"Running command: {command}")
        try:
            self.process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
            print(f"Process started with PID: {self.process.pid}")
        except Exception as e:
            print(f"Error starting process: {e}")

    def _stop_command(self):
        """Stops the background command."""
        if self.process:
            print(f"Stopping process with PID: {self.process.pid}")
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5) # Give it some time to gracefully exit
                print("Process stopped successfully.")
            except subprocess.TimeoutExpired:
                print("Process did not terminate gracefully, killing it.")
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except Exception as e:
                print(f"Error stopping process: {e}")
            finally:
                self.process = None

    def _restart_command(self):
        """Stops and restarts the command."""
        print("Restarting command...")
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

    def stop(self):
        """Stops the command and cancels the restart timer."""
        self._stop_command()
        if self.timer:
            self.timer.cancel()
        print("Background process manager stopped.")


if __name__ == "__main__":
    # Example usage:
    command_template = "ffmpeg -rtsp_transport tcp -i %(ENV_INPUT_STREAM)s -f flv -c:v copy -c:a copy %(ENV_OUTPUT_STREAM)s"
    load_dotenv()
    # Get the environment variables or use defaults.
    input_stream = os.environ.get("ENV_INPUT_STREAM", "rtsp://your_input_stream")
    output_stream = os.environ.get("ENV_OUTPUT_STREAM", "rtmp://your_output_stream")


    manager = BackgroundProcessManager(command_template, input_stream, output_stream)
    manager.start()

    try:
        # Keep the main thread alive to allow the background thread to run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping...")
        manager.stop()
