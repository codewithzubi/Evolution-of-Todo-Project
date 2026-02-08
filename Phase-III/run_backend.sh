#!/bin/bash

# Backend Startup Script
# This script starts the FastAPI backend server with Neon database configuration

echo "🚀 Starting Task CRUD API Backend..."
echo "📊 Using Neon PostgreSQL Database"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit 1

# Export environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Verify database connection
echo "🔗 Testing Neon database connection..."
python3 << 'PYTHON_EOF'
import asyncio
from src.database import engine

async def test_connection():
    try:
        async with engine.connect() as conn:
            print("✅ Neon database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

result = asyncio.run(test_connection())
exit(0 if result else 1)
PYTHON_EOF

if [ $? -ne 0 ]; then
    echo "❌ Could not connect to Neon database. Check your .env file."
    exit 1
fi

echo ""
echo "✅ All checks passed!"
echo "🌐 Backend starting on http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
