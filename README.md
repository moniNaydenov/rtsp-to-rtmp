# FFMPEG Stream Manager for Raspberry Pi 4

This project provides a Dockerized solution for continuously streaming video using FFMPEG on a Raspberry Pi 4. It automatically restarts the FFMPEG process every 15 minutes to maintain a stable stream.

## Overview

The core of the project is a Python script (`ffmpeg_manager.py`) that manages the FFMPEG process. It uses `subprocess` to run FFMPEG in the background and `threading.Timer` to schedule periodic restarts. The script is containerized using Docker for easy deployment and portability.

## Prerequisites

*   **Raspberry Pi 4:**  This project is designed for the Raspberry Pi 4 (64-bit OS recommended).
*   **Docker:** Install Docker on your Raspberry Pi 4:
    ```bash
    curl -fsSL [https://get.docker.com](https://get.docker.com) -o get-docker.sh
    sudo sh get-docker.sh
    ```
*   **Git:** (Optional, but recommended) For cloning this repository.

## Getting Started

1.  **Clone the Repository (Optional):**

    ```bash
    git clone <your_repository_url>
    cd <repository_name>
    ```

2.  **Create a `.env` file:**

    Create a file named `.env` in the project's root directory. This file will store your stream URLs. **Do not commit this file to your repository.**

    Add the following content to your `.env` file, replacing the placeholders with your actual stream URLs:

    ```
    ENV_INPUT_STREAM=rtsp://your_input_stream
    ENV_OUTPUT_STREAM=rtmp://your_output_stream
    ```

    You can use the provided `.env.example` as a template:

    ```bash
    cp .env.example .env
    # Now edit the .env file and put in your actual stream URLs
    nano .env
    ```

3.  **Build the Docker Image:**

    ```bash
    docker build -t ffmpeg-manager-rpi .
    ```

4.  **Run the Docker Container:**

    ```bash
    docker run -d \
      --name rtsp-to-youtube \
      --restart=unless-stopped \
      -v /path/to/your/logs:/app/logs \
      ffmpeg-manager-rpi
    ```

    *   **`-d`:** Runs the container in detached mode (background).
    *   **`--name rtsp-to-youtube`:** Assigns a name to your container.
    *   **`--restart=unless-stopped`:** Restarts the container automatically if it crashes (but not if manually stopped).
    *   **`-v /path/to/your/logs:/app/logs`:** Mounts a local directory for logs (optional but recommended). Replace `/path/to/your/logs` with your desired log directory.
    *   **`ffmpeg-manager-rpi`:** The name of the Docker image you built.

## Using Docker Compose (Recommended for Production)

1.  **Create `docker-compose.yml`:**

    A `docker-compose.yml` file is included in the repository. Make sure you edit it to set up logging properly by modifying the volume path.

2.  **Start the Container:**

    ```bash
    docker-compose up -d
    ```

3.  **Stop the Container:**

    ```bash
    docker-compose down
    ```

## Managing the Container

*   **View Logs:**

    ```bash
    docker logs rtsp-to-youtube
    ```

    or, to follow logs in real-time:

    ```bash
    docker logs -f rtsp-to-youtube
    ```

*   **Stop the Container:**

    ```bash
    docker stop rtsp-to-youtube
    ```

*   **Start the Container:**

    ```bash
    docker start rtsp-to-youtube
    ```

*   **Remove the Container:**

    ```bash
    docker stop rtsp-to-youtube
    docker rm rtsp-to-youtube
    ```

*   **Enter a shell inside the running container:**
    ```bash
    docker exec -it rtsp-to-youtube bash
    ```

## Important Notes

*   **Environment Variables:** Your stream URLs are stored in the `.env` file, which is **not** committed to the repository for security reasons. You must create this file and configure it on your Raspberry Pi.
*   **FFMPEG Installation:** The `Dockerfile` installs FFMPEG.
*   **Resource Usage:** Monitor CPU, memory, and temperature on your Raspberry Pi 4. Long-running FFMPEG processes can be resource-intensive. Consider using hardware acceleration if necessary and ensure proper cooling.
*   **Error Handling:** The Python script includes basic error handling, but consider adding more robust error checking and logging for production use.
*   **Security:** Be mindful of the security implications of running FFMPEG with remote streams, especially if dealing with sensitive content.

## Troubleshooting

*   **Container not starting:**
    *   Check the Docker logs (`docker logs rtsp-to-youtube`).
    *   Verify your `.env` file is correctly formatted and in the right location.
    *   Ensure Docker is running properly on your Raspberry Pi.
*   **FFMPEG errors:**
    *   Check the FFMPEG logs (you might need to add more logging to the `ffmpeg_manager.py` script).
    *   Double-check your input and output stream URLs.
    *   Make sure the necessary codecs are supported by your FFMPEG build.
*   **Performance issues:**
    *   Monitor CPU and memory usage.
    *   Consider adjusting FFMPEG settings (bitrate, resolution).
    *   Investigate hardware-accelerated encoding/decoding.
    *   Ensure your Raspberry Pi has adequate cooling.


