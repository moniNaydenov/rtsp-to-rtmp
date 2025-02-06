# Use a base image optimized for Raspberry Pi (ARM64 architecture)
# Use a base image compatible with ARM64/v8 (Raspberry Pi 4)
FROM balenalib/raspberrypi4-64-python:3.9-buster

# Install ffmpeg (using the arm64 architecture)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install python-dotenv

RUN pip install psutil

# Set the working directory
WORKDIR /app

# Copy the Python script
COPY ffmpeg_manager.py .
COPY .env .


# Set default environment variables
ENV PYTHONUNBUFFERED=1

# Command to run when the container starts
CMD ["python", "-u", "ffmpeg_manager.py"]
