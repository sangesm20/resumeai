# Python base image
FROM python:3.10-slim

# Install Poppler and Tesseract for PDF OCR
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Command to run the FastAPI app on Render
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]