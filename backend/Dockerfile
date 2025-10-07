# Use the appropriate base image for your application (e.g., python:3.10-slim)
FROM python:3.10-slim

# Install the PostgreSQL client, dos2unix, and curl for the healthcheck
RUN apt-get update && apt-get install -y postgresql-client dos2unix curl && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the dependency files first to leverage caching
COPY ./requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy the application code explicitly ---
COPY ./alembic.ini /app/alembic.ini
COPY ./entrypoint.sh /app/entrypoint.sh
COPY ./app /app/app
#
# REMOVED THIS LINE --> COPY ./migrations /app/migrations
#

# --- CORRECTION APPLIED HERE ---
# 1. Create the captures directory so it exists in the container
RUN mkdir -p /app/captures

# Correct the line ending format of the entrypoint
RUN dos2unix /app/entrypoint.sh

# 2. Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# The command to be executed by the entrypoint (CMD)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]