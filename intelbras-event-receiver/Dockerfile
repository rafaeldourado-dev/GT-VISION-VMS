# Use a python image as a base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY intelbras_event_receiver.py .

# Specify the command to run on container start
CMD ["python", "intelbras_event_receiver.py"]


