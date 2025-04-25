FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add gunicorn
RUN pip install gunicorn==21.2.0

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8080

# Run the web service on container startup
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app 