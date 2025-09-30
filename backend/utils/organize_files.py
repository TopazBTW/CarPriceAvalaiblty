#!/usr/bin/env python3
"""
🗂️ BACKEND FOLDER ORGANIZATION SCRIPT
Organize all backend files into appropriate folders
"""

import os
import shutil
from pathlib import Path

def organize_backend_files():
    """Organize all backend files into proper folder structure"""
    
    backend_dir = Path('.')
    
    print("🗂️ ORGANIZING BACKEND FILES INTO FOLDERS")
    print("=" * 50)
    
    # Define file categories and their target folders
    file_organization = {
        'scrapers': [
            'advanced_morocco_scraper.py',
            'comprehensive_scraper.py', 
            'enhanced_scrapers.py',
            'production_scraper.py',
            'robust_morocco_scraper.py',
            'scrapers.py',
            'wandaloo_scraper.py',
            'real_morocco_prices.py'
        ],
        'data/json': [
            'car_data_clean_final.json',
            'scraped_wandaloo_clean.json',
            'scraped_wandaloo_clean_clean.json', 
            'scraped_wandaloo_followed.json',
            'scraped_wandaloo_followed_clean.json'
        ],
        'data/csv': [
            'sample_car_data.csv'
        ],
        'data/html': [
            'wandaloo_marques.html'
        ],
        'models': [
            'car_price_model.joblib',
            'ml_model.py'
        ],
        'tests': [
            'test_advanced_scraper.py',
            'test_api.py', 
            'test_clean_backend.py',
            'test_endpoints.py',
            'test_scraper.py',
            'test_server.py',
            'final_demo.py',
            'final_cleanup_summary.py'
        ],
        'utils': [
            'cleanup_json.py',
            'cleanup_report.txt',
            'comprehensive_backend_cleanup.py',
            'create_perfect_car_data.py',
            'generate_sample_data.py',
            'run_wandaloo_clean.py',
            'run_wandaloo_follow.py', 
            'run_wandaloo_follow_links.py',
            'tmp_scrape.py',
            'tmp_scrape_clean.py',
            'summarize_scrape.py'
        ],
        'config': [
            'config.py',
            'requirements.txt',
            'requirements_clean.txt'
        ],
        'deployment': [
            'docker-compose.yml',
            'Dockerfile',
            'start.bat'
        ]
    }
    
    # Create folders and move files
    moved_count = 0
    
    for folder, files in file_organization.items():
        # Create folder if it doesn't exist
        target_dir = backend_dir / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\\n📁 Moving files to {folder}/")
        print("-" * 30)
        
        for filename in files:
            source_file = backend_dir / filename
            target_file = target_dir / filename
            
            if source_file.exists():
                try:
                    shutil.move(str(source_file), str(target_file))
                    print(f"   ✅ {filename}")
                    moved_count += 1
                except Exception as e:
                    print(f"   ❌ {filename} - Error: {e}")
            else:
                print(f"   ⚠️  {filename} - Not found")
    
    print(f"\\n📊 ORGANIZATION SUMMARY:")
    print("-" * 25)
    print(f"✅ Total files moved: {moved_count}")
    print(f"📂 Folders created: {len(file_organization)}")
    
    # Show final structure
    print(f"\\n🌳 FINAL BACKEND STRUCTURE:")
    print("-" * 35)
    
    for folder in file_organization.keys():
        folder_path = backend_dir / folder
        if folder_path.exists():
            file_count = len(list(folder_path.glob('*')))
            print(f"📁 {folder}/ ({file_count} files)")
    
    # Show remaining root files
    root_files = [f for f in backend_dir.iterdir() 
                  if f.is_file() and not f.name.startswith('.') and not f.name.startswith('__')]
    
    if root_files:
        print(f"\\n📄 FILES REMAINING IN ROOT:")
        print("-" * 30)
        for file in root_files:
            print(f"   📄 {file.name}")
    
    print(f"\\n🎉 BACKEND ORGANIZATION COMPLETE!")
    
    return moved_count

if __name__ == "__main__":
    organize_backend_files()