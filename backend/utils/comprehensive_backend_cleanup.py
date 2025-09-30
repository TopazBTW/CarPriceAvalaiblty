#!/usr/bin/env python3
"""
🧹 COMPREHENSIVE BACKEND & JSON CLEANUP
Fixes all issues in the Morocco car valuation backend
"""

import json
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendCleanupTool:
    """Comprehensive tool to clean up backend and JSON data"""
    
    def __init__(self, backend_dir: str):
        self.backend_dir = Path(backend_dir)
        self.issues_found = []
        self.fixes_applied = []
        
    def identify_navigation_items(self) -> List[str]:
        """Identify common navigation items that should be filtered out"""
        return [
            'Guide D Achat', 'guide d achat', 'GUIDE D ACHAT',
            'Nouveaté S', 'nouveauté s', 'NOUVEAUTÉ S', 'Nouveautés',
            'Prochainement AU Maroc', 'prochainement au maroc', 'PROCHAINEMENT AU MAROC',
            'Concessionnaires', 'concessionnaires', 'CONCESSIONNAIRES',
            'Concessionnaires Automobile', 'concessionnaires automobile',
            'Tarifs ET Budget', 'tarifs et budget', 'TARIFS ET BUDGET',
            'Trouver UN Concessionnaire', 'trouver un concessionnaire',
            'Actualités', 'actualités', 'ACTUALITÉS',
            'Comparateur', 'comparateur', 'COMPARATEUR',
            'Financement', 'financement', 'FINANCEMENT',
            'Assurance', 'assurance', 'ASSURANCE',
            'Service Après Vente', 'service après vente',
            'Pièces Détachées', 'pièces détachées',
            'Entretien', 'entretien', 'ENTRETIEN',
            'Garantie', 'garantie', 'GARANTIE'
        ]
    
    def is_valid_car_model(self, model_name: str) -> bool:
        """Check if a string represents a valid car model"""
        if not model_name or len(model_name.strip()) < 2:
            return False
            
        model = model_name.strip().lower()
        
        # Filter out navigation items
        nav_items = [item.lower() for item in self.identify_navigation_items()]
        if model in nav_items:
            return False
            
        # Filter out generic terms
        generic_terms = [
            'home', 'accueil', 'contact', 'about', 'à propos',
            'services', 'produits', 'gamme', 'catalogue',
            'news', 'actualités', 'blog', 'media', 'presse',
            'carrières', 'emploi', 'recrutement',
            'mentions légales', 'politique de confidentialité',
            'cookies', 'cgv', 'cgu', 'newsletter',
            'facebook', 'twitter', 'instagram', 'youtube',
            'linkedin', 'social', 'partager', 'suivre'
        ]
        
        if model in generic_terms:
            return False
            
        # Filter out URLs or URL-like strings
        if any(char in model for char in ['/', '.com', '.ma', 'http', 'www']):
            return False
            
        # Filter out very generic car-related terms
        generic_car_terms = [
            'voiture', 'véhicule', 'auto', 'automobile',
            'neuf', 'occasion', 'prix', 'tarif',
            'essai', 'test', 'review', 'avis'
        ]
        
        if model in generic_car_terms:
            return False
            
        return True
    
    def is_valid_price(self, price: Any) -> bool:
        """Check if a price value is valid"""
        if price is None:
            return False
            
        try:
            price_num = float(price)
            # Valid car prices in Morocco (MAD): 50,000 to 5,000,000
            return 50000 <= price_num <= 5000000
        except (ValueError, TypeError):
            return False
    
    def clean_scraped_json(self, json_file: str) -> Dict[str, Any]:
        """Clean the scraped JSON data"""
        logger.info(f"🧹 Cleaning JSON file: {json_file}")
        
        if not os.path.exists(json_file):
            logger.warning(f"File not found: {json_file}")
            return {}
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
            return {}
        
        cleaned_data = {}
        total_entries = 0
        cleaned_entries = 0
        removed_entries = 0
        
        for brand, models in data.items():
            if not isinstance(models, dict):
                continue
                
            cleaned_models = {}
            
            for model_name, listings in models.items():
                total_entries += 1
                
                # Check if this is a valid car model
                if not self.is_valid_car_model(model_name):
                    removed_entries += 1
                    self.issues_found.append(f"Removed invalid model: {model_name}")
                    continue
                
                if not isinstance(listings, list):
                    removed_entries += 1
                    continue
                
                # Clean listings for this model
                cleaned_listings = []
                for listing in listings:
                    if not isinstance(listing, dict):
                        continue
                        
                    # Validate price
                    if not self.is_valid_price(listing.get('price')):
                        continue
                    
                    # Validate title
                    title = listing.get('title', '').strip()
                    if not title or not self.is_valid_car_model(title.split()[0] if title else ''):
                        continue
                    
                    # Validate URL
                    url = listing.get('url', '')
                    if not url or 'wandaloo.com' not in url:
                        continue
                    
                    cleaned_listings.append(listing)
                
                if cleaned_listings:
                    cleaned_models[model_name] = cleaned_listings
                    cleaned_entries += 1
                else:
                    removed_entries += 1
            
            if cleaned_models:
                cleaned_data[brand] = cleaned_models
        
        # Save cleaned data
        clean_file = json_file.replace('.json', '_clean.json')
        with open(clean_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ JSON cleanup complete!")
        logger.info(f"📊 Total entries processed: {total_entries}")
        logger.info(f"✅ Clean entries kept: {cleaned_entries}")
        logger.info(f"🗑️  Invalid entries removed: {removed_entries}")
        logger.info(f"📁 Clean file saved as: {clean_file}")
        
        self.fixes_applied.append(f"Cleaned JSON: {removed_entries} invalid entries removed")
        
        return cleaned_data
    
    def remove_duplicate_files(self):
        """Remove duplicate and redundant backend files"""
        logger.info("🧹 Removing duplicate and redundant files...")
        
        # Files to remove (duplicates, temp files, outdated)
        files_to_remove = [
            'comprehensive_cleanup.py',
            'tmp_scrape.py',
            'tmp_scrape_clean.py',
            'run_wandaloo_clean.py',
            'run_wandaloo_follow.py',
            'run_wandaloo_follow_links.py',
            'test_server.py',
            'summarize_scrape.py',
            'scraped_wandaloo_followed_sample.json',
            'Car.code-workspace',
            'frontend_integration.ts',  # This should be in frontend
            'Attached HTML and CSS Context.txt'  # Not needed
        ]
        
        removed_count = 0
        for filename in files_to_remove:
            file_path = self.backend_dir / filename
            if file_path.exists():
                try:
                    file_path.unlink()
                    removed_count += 1
                    logger.info(f"🗑️  Removed: {filename}")
                    self.fixes_applied.append(f"Removed redundant file: {filename}")
                except Exception as e:
                    logger.warning(f"Could not remove {filename}: {e}")
        
        logger.info(f"✅ Removed {removed_count} redundant files")
    
    def clean_pycache(self):
        """Clean up Python cache files"""
        logger.info("🧹 Cleaning Python cache...")
        
        pycache_dir = self.backend_dir / '__pycache__'
        if pycache_dir.exists():
            import shutil
            try:
                shutil.rmtree(pycache_dir)
                logger.info("🗑️  Removed __pycache__ directory")
                self.fixes_applied.append("Cleaned Python cache")
            except Exception as e:
                logger.warning(f"Could not remove __pycache__: {e}")
    
    def validate_main_py(self):
        """Validate and report on main.py issues"""
        logger.info("🔍 Validating main.py...")
        
        main_file = self.backend_dir / 'main.py'
        if not main_file.exists():
            self.issues_found.append("main.py file not found!")
            return
        
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for duplicate imports
            imports = re.findall(r'^(from .+ import .+|import .+)$', content, re.MULTILINE)
            seen_imports = set()
            duplicate_imports = []
            
            for imp in imports:
                if imp in seen_imports:
                    duplicate_imports.append(imp)
                seen_imports.add(imp)
            
            if duplicate_imports:
                self.issues_found.extend([f"Duplicate import: {imp}" for imp in duplicate_imports])
            
            # Check for unused functions (basic check)
            function_definitions = re.findall(r'^def (\w+)', content, re.MULTILINE)
            function_calls = re.findall(r'(\w+)\(', content)
            
            unused_functions = []
            for func in function_definitions:
                if func not in function_calls or content.count(func) <= 1:
                    unused_functions.append(func)
            
            if unused_functions:
                self.issues_found.extend([f"Potentially unused function: {func}" for func in unused_functions])
            
            logger.info(f"✅ main.py validation complete")
            if duplicate_imports:
                logger.warning(f"⚠️  Found {len(duplicate_imports)} duplicate imports")
            if unused_functions:
                logger.warning(f"⚠️  Found {len(unused_functions)} potentially unused functions")
                
        except Exception as e:
            self.issues_found.append(f"Error validating main.py: {e}")
    
    def create_clean_requirements(self):
        """Create a clean requirements.txt with only necessary dependencies"""
        logger.info("📦 Creating clean requirements.txt...")
        
        essential_packages = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "pydantic==2.5.0",
            "pandas==2.1.3",
            "scikit-learn==1.3.2",
            "joblib==1.3.2",
            "aiohttp==3.9.1",
            "beautifulsoup4==4.12.2",
            "lxml==4.9.3",
            "requests==2.31.0",
            "cachetools==5.3.2",
            "python-multipart==0.0.6"
        ]
        
        requirements_file = self.backend_dir / 'requirements_clean.txt'
        with open(requirements_file, 'w') as f:
            f.write('\n'.join(essential_packages))
        
        logger.info(f"✅ Clean requirements saved to: {requirements_file}")
        self.fixes_applied.append("Created clean requirements.txt")
    
    def run_comprehensive_cleanup(self):
        """Run all cleanup operations"""
        logger.info("🚀 Starting comprehensive backend cleanup...")
        logger.info("=" * 60)
        
        # 1. Clean JSON data
        json_files = [
            'scraped_wandaloo_followed.json',
            'scraped_wandaloo_clean.json'
        ]
        
        for json_file in json_files:
            json_path = self.backend_dir / json_file
            if json_path.exists():
                self.clean_scraped_json(str(json_path))
        
        # 2. Remove duplicate files
        self.remove_duplicate_files()
        
        # 3. Clean Python cache
        self.clean_pycache()
        
        # 4. Validate main.py
        self.validate_main_py()
        
        # 5. Create clean requirements
        self.create_clean_requirements()
        
        # Generate cleanup report
        self.generate_cleanup_report()
        
        logger.info("🏁 Comprehensive cleanup complete!")
        logger.info("=" * 60)
    
    def generate_cleanup_report(self):
        """Generate a comprehensive cleanup report"""
        logger.info("\n📋 CLEANUP REPORT")
        logger.info("=" * 40)
        
        logger.info(f"🔍 Issues Found: {len(self.issues_found)}")
        for issue in self.issues_found[:10]:  # Show first 10 issues
            logger.info(f"   ⚠️  {issue}")
        if len(self.issues_found) > 10:
            logger.info(f"   ... and {len(self.issues_found) - 10} more issues")
        
        logger.info(f"\n✅ Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            logger.info(f"   🔧 {fix}")
        
        # Save report to file
        report_file = self.backend_dir / 'cleanup_report.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("MOROCCO CAR VALUATION - BACKEND CLEANUP REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Issues Found ({len(self.issues_found)}):\n")
            f.write("-" * 30 + "\n")
            for issue in self.issues_found:
                f.write(f"⚠️  {issue}\n")
            
            f.write(f"\nFixes Applied ({len(self.fixes_applied)}):\n")
            f.write("-" * 30 + "\n")
            for fix in self.fixes_applied:
                f.write(f"✅ {fix}\n")
        
        logger.info(f"\n📄 Full report saved to: {report_file}")

def main():
    """Main cleanup function"""
    backend_dir = "c:\\Users\\berse\\Desktop\\Car\\morocco-car-valuation (2)\\backend"
    
    cleanup_tool = BackendCleanupTool(backend_dir)
    cleanup_tool.run_comprehensive_cleanup()
    
    print("\n🎉 BACKEND CLEANUP COMPLETE! 🎉")
    print("Your backend is now clean and optimized!")

if __name__ == "__main__":
    main()