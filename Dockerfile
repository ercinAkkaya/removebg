FROM python:3.10-slim-bookworm

# Install necessary system dependencies for image processing (cv2/pillow often need these)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install python dependencies inside the container
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# PERFORMANCE OPTIMIZATION
# -----------------------------------------------------------------------------
# Run a one-liner to pre-download the model into the container.
# This ensures the model is "baked in" to the Docker image, avoiding
# download delays or timeouts during Cloud Run cold starts.
RUN python -c "from rembg import new_session; new_session('birefnet-general')"

# Copy the rest of the application code
COPY . .

# Expose port 8080
EXPOSE 8080

# Start the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
