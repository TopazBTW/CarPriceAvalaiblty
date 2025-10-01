#!/usr/bin/env python3
"""
🚗 START KIFAL API SERVER
"""

import os
import sys

# Change to backend directory
backend_dir = r"c:\Users\berse\Desktop\Car\morocco-car-valuation (2)\backend"
os.chdir(backend_dir)

# Add to Python path
sys.path.insert(0, backend_dir)

# Import and run
if __name__ == "__main__":
    import uvicorn
    from main_kifal import app
    
    print("🚗 MOROCCO CAR VALUATION API - KIFAL.MA DATA")
    print("=" * 50)
    print("📊 Data Source: https://neuf.kifal.ma/")
    print("🌐 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔥 Starting server...")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)