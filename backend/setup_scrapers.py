#!/usr/bin/env python3
"""
Setup script for used cars scraping system
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing Scrapy and dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements_scrapy.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Successfully installed all dependencies")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_scrapy_cfg():
    """Create scrapy.cfg file"""
    scrapy_cfg_content = """[settings]
default = scrapy_project.settings

[deploy]
project = morocco_cars
"""
    
    cfg_path = Path(__file__).parent / "scrapy.cfg"
    
    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.write(scrapy_cfg_content)
    
    print("✅ Created scrapy.cfg configuration file")

def test_scrapy_installation():
    """Test if Scrapy is properly installed"""
    try:
        import scrapy
        print(f"✅ Scrapy version {scrapy.__version__} installed successfully")
        return True
    except ImportError:
        print("❌ Scrapy installation failed")
        return False

def setup_project_structure():
    """Ensure all directories exist"""
    directories = [
        Path(__file__).parent / "scrapy_project",
        Path(__file__).parent / "scrapy_project" / "spiders",
        Path(__file__).parent / "data" / "csv",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ Project structure created")

def main():
    """Main setup function"""
    print("🚗 Setting up Morocco Used Cars Scraping System")
    print("=" * 50)
    
    # Setup project structure
    setup_project_structure()
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed - could not install requirements")
        return False
    
    # Test installation
    if not test_scrapy_installation():
        print("❌ Setup failed - Scrapy not properly installed")
        return False
    
    # Create scrapy config
    create_scrapy_cfg()
    
    print("\n🎉 SETUP COMPLETE!")
    print("\n📋 Next steps:")
    print("   1. Start the used cars API server:")
    print("      python used_cars_api.py")
    print("\n   2. Test the scrapers:")
    print("      curl http://localhost:8001/test-scrapers")
    print("\n   3. Search for cars from your frontend:")
    print("      POST http://localhost:8001/search-cars")
    print("      GET http://localhost:8001/scraped-results")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)