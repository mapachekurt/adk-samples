# Dockerfile for Agent Builder Pro

# 1. Base Image
# Use an official Python runtime as a parent image.
# python:3.10-slim is a lightweight and secure choice.
FROM python:3.10-slim

# 2. Set Environment Variables
# Prevents Python from writing pyc files to disc and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set Working Directory
# All subsequent commands will be run from this directory
WORKDIR /app

# 4. Install Dependencies
# First, copy only the requirements.txt file to leverage Docker's layer caching.
# This layer is only rebuilt if requirements.txt changes.
COPY requirements.txt .

# Upgrade pip and install the Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code
# Copy the entire project directory into the container.
# The .dockerignore file will exclude unnecessary files.
COPY . .

# 6. Expose Port
# The ADK web server runs on port 8000 by default.
# This informs Docker that the container listens on this network port.
EXPOSE 8000

# 7. Define Entrypoint
# This is the command that will be executed when the container starts.
# It starts the ADK server, pointing to the root_agent object.
# --host 0.0.0.0 makes the server accessible from outside the container.
CMD ["adk", "serve", "agent_builder_pro.agent.root_agent", "--host", "0.0.0.0", "--port", "8000"]
