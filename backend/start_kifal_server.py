#!/usr/bin/env python3
"""
🚗 START KIFAL API SERVER
"""

import os
import sys

# Change to backend directory
# Use current script directory as backend dir (works in workspace)
backend_dir = os.path.dirname(os.path.abspath(__file__))
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