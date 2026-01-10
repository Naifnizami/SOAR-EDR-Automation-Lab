# 1. Use an official lightweight Python runtime as a parent image
FROM python:3.10-slim

# 2. Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Install System Security Tools (Nmap, etc.)
# Even if you aren't using them yet, a "Security Analyst" agent needs them available.
RUN apt-get update && apt-get install -y \
    nmap \
    curl \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# 4. Set work directory inside the container
WORKDIR /app

# 5. Install Dependencies
# Copy only requirements first to cache this layer (makes rebuilds faster)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the source code into the container
COPY src/ ./src/
COPY config/ ./config/

# 7. Create a non-root user for security (Crucial for "Production Level")
RUN useradd -m appuser
USER appuser

# 8. Expose the port Flask runs on
EXPOSE 5000

# 9. Run the application
# We use src.main because we are in /app
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "src.main:app"]
