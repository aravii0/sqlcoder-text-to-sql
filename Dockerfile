# Dockerfile for SQLCoder Text-to-SQL Application
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize database
RUN cd database && python init_db.py --force

# Expose ports
EXPOSE 8000 8501

# Create startup script
RUN echo '#!/bin/bash\n\
cd /app/backend && python main.py &\n\
cd /app/frontend && streamlit run app.py --server.address 0.0.0.0 --server.port 8501\n\
wait' > start.sh && chmod +x start.sh

# Start application
CMD ["./start.sh"]
