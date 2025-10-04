#!/usr/bin/env python3
"""
Start Morocco Car API Server
"""
import uvicorn

if __name__ == "__main__":
    print("🚗 Starting Morocco Car Price API...")
    print("📡 Server: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("📊 Dataset: 10,000 Morocco cars")
    print("\n✅ Server running! Press CTRL+C to stop.\n")
    
    uvicorn.run(
        "used_cars_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
