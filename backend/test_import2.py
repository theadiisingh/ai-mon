"""Quick test to check if backend imports work."""
import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
    print("SUCCESS: Backend imports work correctly!")
    print(f"App: {app}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

