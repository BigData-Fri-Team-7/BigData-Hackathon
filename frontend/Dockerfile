# Use an official Python runtime as the base image
FROM python:3.9-slim

# Disable .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip and install required packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Run the Streamlit app on port 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.enableCORS=false", "--server.port", "8501"]
