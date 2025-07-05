# Base image: Python 3.9
FROM python:3.9-slim

# Install Node.js and Puppeteer dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    chromium \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Puppeteer
RUN npm install -g puppeteer puppeteer-extra puppeteer-extra-plugin-stealth

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app files
COPY . /app
WORKDIR /app

# Expose Streamlit port
EXPOSE 8501

# Start Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
