#!/usr/bin/env python3
"""
Test script to check for import issues and "AI future disabled" errors
"""

print("🔍 Testing Python imports and checking for errors...")

try:
    print("✅ Testing basic imports...")
    import os
    import sys
    import json
    import sqlite3
    print("✅ Basic imports successful")
    
    print("✅ Testing FastAPI imports...")
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ FastAPI imports successful")
    
    print("✅ Testing SQLAlchemy imports...")
    from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    print("✅ SQLAlchemy imports successful")
    
    print("✅ Testing OpenAI imports...")
    import openai
    print("✅ OpenAI imports successful")
    
    print("✅ Testing Pydantic imports...")
    from pydantic import BaseModel
    from pydantic_settings import BaseSettings
    print("✅ Pydantic imports successful")
    
    print("✅ Testing backend modules...")
    import sys
    sys.path.append('backend')
    
    from core.config import settings
    print("✅ Backend config import successful")
    
    from core.db import get_db
    print("✅ Backend database import successful")
    
    from models.log import ChatLog
    print("✅ Backend models import successful")
    
    print("🎉 All imports successful! No 'AI future disabled' errors found.")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("This might be causing the 'AI future disabled' error.")
    
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    print("This might be causing the 'AI future disabled' error.")

print("\n🔍 Checking Python version...")
print(f"Python version: {sys.version}")

print("\n🔍 Checking if we're in the right directory...")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

print("\n✅ Test completed!")
