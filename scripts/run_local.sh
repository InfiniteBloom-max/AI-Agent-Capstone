#!/bin/bash
# Start the orchestrator
uvicorn services.orchestrator.app:app --reload --port 8000
