#!/bin/bash

# Start Redis server in the background
redis-server &

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
