FROM --platform=linux/amd64 python:3.13.2-slim

# Set environment variables to avoid creating .pyc files and to ensure output is flushed immediately
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Run the application
CMD ["python", "main.py"]
