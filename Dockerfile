# Use a base image optimized for Raspberry Pi (ARM64 architecture)
# Use a base image compatible with ARM64/v8 (Raspberry Pi 4)
FROM balenalib/raspberrypi4-64-python:3.9-buster

# Install ffmpeg (using the arm64 architecture)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install python-dotenv

# Set the working directory
WORKDIR /app

# Copy the Python script
COPY ffmpeg_manager.py .

# Set default environment variables
ENV ENV_INPUT_STREAM="rtsp://your_input_stream"
ENV ENV_OUTPUT_STREAM="rtmp://your_output_stream"

# Command to run when the container starts
CMD ["python", "ffmpeg_manager.py"]
