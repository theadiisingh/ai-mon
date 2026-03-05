"""
Vercel Serverless API Handler

This module provides the serverless handler for Vercel deployment.
It wraps the FastAPI application to work with Vercel's serverless functions.
"""
import os
import sys

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set environment to production for Vercel
os.environ["VERCEL"] = "true"
os.environ["ENVIRONMENT"] = "production"
os.environ["DEBUG"] = "false"

# Now import and create the ASGI app
from app.main import app

# Vercel expects an ASGI app callable
handler = app

