FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    default-mysql-client build-essential libssl-dev netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


# Set workdir
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Add script to wait for MySQL
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# runs after db is ready
CMD ["/wait-for-db.sh", "db", "3306", "python", "-m", "src.main", "--auto-month-end"]
