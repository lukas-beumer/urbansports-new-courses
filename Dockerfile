# Use the official Python image from the Docker Hub
FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright and its dependencies
RUN playwright install

# Copy the rest of the application code into the container
COPY . .

# Run the application
CMD ["python", "main.py"]