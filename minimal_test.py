print("Hello World")
print("Testing Python execution")

try:
    import sys
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path}")
except Exception as e:
    print(f"Error: {e}")

try:
    import sqlite3
    print("SQLite3 module available")
except Exception as e:
    print(f"SQLite3 error: {e}")

try:
    import fastapi
    print("FastAPI module available")
except Exception as e:
    print(f"FastAPI error: {e}")

print("Test completed")
