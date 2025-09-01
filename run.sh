#!/bin/bash

# Run the FastAPI app with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
