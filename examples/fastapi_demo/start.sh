#!/bin/bash
# Startup script for FastAPI application
# Generated from AgentScript source: sample_pipeline.ags

set -e

echo "Starting AgentScript FastAPI application..."

# Wait for database if configured
if [ "${DATABASE_URL:-}" ]; then
    echo "Waiting for database..."
    python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from database import Base

async def wait_for_db():
    engine = create_async_engine('$DATABASE_URL')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

asyncio.run(wait_for_db())
"
fi

# Start the application
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-1}
