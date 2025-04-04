# Start from a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install required system packages including LibreOffice
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-dejavu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app code
COPY . .

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8080

# Expose the Streamlit port
EXPOSE 8080

# Start Streamlit app
CMD ["streamlit", "run", "app.py"]
