FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml .

# Install dependencies using pip
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e .

# Copy source code
COPY ./src ./src

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]