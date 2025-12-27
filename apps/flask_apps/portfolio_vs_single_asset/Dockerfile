# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Make port 8503 available to the world outside this container
EXPOSE 8503

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8503"]
