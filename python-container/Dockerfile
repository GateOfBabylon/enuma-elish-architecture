# Use the official lightweight Python image
FROM python:3.9-slim

# Create and switch to the /app working directory
WORKDIR /app

# Copy your Python scripts
COPY ./scripts /app/scripts

# Copy your requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Default command (will be overridden by Go code)
CMD ["python"]
