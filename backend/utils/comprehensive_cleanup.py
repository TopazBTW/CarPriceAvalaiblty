#!/usr/bin/env python3
"""
🧹 COMPREHENSIVE BACKEND & JSON CLEANUP TOOL
Fixes all identified issues in the backend and JSON data
"""

import json
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendCleaner:
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.issues_found = []
        self.fixes_applied = []
        
    def analyze_json_files(self) -> Dict[str, List[str]]:
        """Analyze JSON files for data quality issues"""
        issues = {}
        
        json_files = list(self.backend_path.glob("*.json"))
        
        for json_file in json_files:
            file_issues = []
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check for navigation noise
                navigation_keywords = [
                    "Guide D Achat", "Nouveaut S", "Prochainement AU Maroc", 
                    "Toutes LES Nouveaut S", "navigation", "menu", "footer",
                    "header", "sidebar", "breadcrumb"
                ]
                
                self._check_navigation_noise(data, file_issues, navigation_keywords)
                self._check_duplicate_entries(data, file_issues)
                self._check_invalid_models(data, file_issues)
                self._check_price_validity(data, file_issues)
                
                if file_issues:
                    issues[json_file.name] = file_issues
                    
            except Exception as e:
                issues[json_file.name] = [f"JSON parsing error: {e}"]
        
        return issues
    
    def _check_navigation_noise(self, data: Any, issues: List[str], keywords: List[str]):
        """Check for navigation/menu items in car data"""
        def scan_object(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Check if key contains navigation keywords
                    for keyword in keywords:
                        if keyword.lower() in key.lower():
                            issues.append(f"Navigation noise at {current_path}: '{key}'")
                    
                    scan_object(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    scan_object(item, f"{path}[{i}]")
        
        scan_object(data)
    
    def _check_duplicate_entries(self, data: Any, issues: List[str]):
        """Check for duplicate car entries"""
        seen_entries = set()
        duplicates = []
        
        def scan_for_duplicates(obj, path=""):
            if isinstance(obj, dict):
                if "title" in obj and "price" in obj and "url" in obj:
                    entry_key = f"{obj.get('title', '')}-{obj.get('price', 0)}"
                    if entry_key in seen_entries:
                        duplicates.append(f"Duplicate at {path}: {obj.get('title', 'Unknown')}")
                    else:
                        seen_entries.add(entry_key)
                
                for key, value in obj.items():
                    scan_for_duplicates(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    scan_for_duplicates(item, f"{path}[{i}]")
        
        scan_for_duplicates(data)
        if duplicates:
            issues.extend(duplicates)
    
    def _check_invalid_models(self, data: Any, issues: List[str]):
        """Check for invalid model names"""
        invalid_patterns = [
            r"guide\s+d\s*achat",
            r"nouveaut.+s",
            r"prochainement",
            r"toutes\s+les",
            r"menu",
            r"navigation"
        ]
        
        def scan_models(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Check if key looks like an invalid model name
                    for pattern in invalid_patterns:
                        if re.search(pattern, key, re.IGNORECASE):
                            issues.append(f"Invalid model name at {current_path}: '{key}'")
                    
                    scan_models(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    scan_models(item, f"{path}[{i}]")
        
        scan_models(data)
    
    def _check_price_validity(self, data: Any, issues: List[str]):
        """Check for invalid prices"""
        def scan_prices(obj, path=""):
            if isinstance(obj, dict):
                if "price" in obj:
                    price = obj["price"]
                    if not isinstance(price, (int, float)) or price <= 0:
                        issues.append(f"Invalid price at {path}: {price}")
                
                for key, value in obj.items():
                    scan_prices(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    scan_prices(item, f"{path}[{i}]")
        
        scan_prices(data)
    
    def clean_json_data(self) -> Dict[str, Any]:
        """Clean all JSON files and create clean versions"""
        results = {}
        
        json_files = [
            "scraped_wandaloo_followed.json",
            "scraped_wandaloo_followed_sample.json"
        ]
        
        for filename in json_files:
            filepath = self.backend_path / filename
            if not filepath.exists():
                continue
                
            logger.info(f"🧹 Cleaning {filename}...")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cleaned_data = self._clean_data_structure(data)
            results[filename] = cleaned_data
            
            # Save cleaned version
            clean_filename = filename.replace('.json', '_cleaned.json')
            clean_filepath = self.backend_path / clean_filename
            
            with open(clean_filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved cleaned version: {clean_filename}")
        
        return results
    
    def _clean_data_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the data structure removing navigation noise"""
        cleaned = {}
        
        # Navigation keywords to remove
        navigation_keywords = [
            "guide d achat", "nouveaut s", "prochainement au maroc",
            "toutes les nouveaut s", "navigation", "menu", "footer",
            "header", "sidebar", "breadcrumb", "accueil", "contact"
        ]
        
        for brand, brand_data in data.items():
            if not isinstance(brand_data, dict):
                continue
            
            cleaned_brand = {}
            
            for model_key, model_data in brand_data.items():
                # Skip navigation entries
                if any(nav in model_key.lower() for nav in navigation_keywords):
                    logger.debug(f"Skipping navigation entry: {model_key}")
                    continue
                
                # Clean model data
                if isinstance(model_data, list):
                    cleaned_listings = []
                    seen_entries = set()
                    
                    for listing in model_data:
                        if not isinstance(listing, dict):
                            continue
                        
                        # Validate listing
                        if not self._is_valid_listing(listing):
                            continue
                        
                        # Remove duplicates
                        listing_key = f"{listing.get('title', '')}-{listing.get('price', 0)}"
                        if listing_key in seen_entries:
                            continue
                        seen_entries.add(listing_key)
                        
                        cleaned_listings.append(listing)
                    
                    if cleaned_listings:
                        cleaned_brand[model_key] = cleaned_listings
            
            if cleaned_brand:
                cleaned[brand] = cleaned_brand
        
        return cleaned
    
    def _is_valid_listing(self, listing: Dict[str, Any]) -> bool:
        """Check if a listing is valid"""
        # Must have title, price, and url
        if not all(key in listing for key in ['title', 'price', 'url']):
            return False
        
        # Price must be valid
        price = listing.get('price')
        if not isinstance(price, (int, float)) or price <= 0:
            return False
        
        # Title shouldn't be navigation text
        title = listing.get('title', '').lower()
        navigation_terms = ['guide', 'nouveauté', 'prochainement', 'toutes les']
        if any(term in title for term in navigation_terms):
            return False
        
        return True
    
    def analyze_backend_files(self) -> Dict[str, List[str]]:
        """Analyze backend files for redundancy and issues"""
        issues = {}
        
        # Check for redundant files
        python_files = list(self.backend_path.glob("*.py"))
        
        # Group files by functionality
        scraper_files = [f for f in python_files if 'scraper' in f.name.lower()]
        test_files = [f for f in python_files if 'test' in f.name.lower()]
        temp_files = [f for f in python_files if f.name.startswith('tmp_')]
        run_files = [f for f in python_files if f.name.startswith('run_')]
        
        if len(scraper_files) > 3:
            issues['redundant_scrapers'] = [f.name for f in scraper_files]
        
        if len(test_files) > 3:
            issues['redundant_tests'] = [f.name for f in test_files]
        
        if temp_files:
            issues['temporary_files'] = [f.name for f in temp_files]
        
        if len(run_files) > 2:
            issues['redundant_runners'] = [f.name for f in run_files]
        
        return issues
    
    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        logger.info("🔍 ANALYZING BACKEND & JSON DATA...")
        
        # Analyze JSON files
        json_issues = self.analyze_json_files()
        
        # Analyze backend files
        backend_issues = self.analyze_backend_files()
        
        # Generate report
        print("🧹 COMPREHENSIVE CLEANUP REPORT")
        print("=" * 50)
        
        if json_issues:
            print("\n📊 JSON DATA ISSUES:")
            for filename, issues in json_issues.items():
                print(f"\n📄 {filename}:")
                for issue in issues[:10]:  # Show first 10 issues
                    print(f"   • {issue}")
                if len(issues) > 10:
                    print(f"   ... and {len(issues) - 10} more issues")
        
        if backend_issues:
            print("\n🗂️ BACKEND FILE ISSUES:")
            for category, files in backend_issues.items():
                print(f"\n📁 {category.replace('_', ' ').title()}:")
                for file in files:
                    print(f"   • {file}")
        
        # Clean JSON data
        print("\n🧹 CLEANING JSON DATA...")
        cleaned_results = self.clean_json_data()
        
        print(f"\n✅ CLEANUP COMPLETED!")
        print(f"📊 JSON files processed: {len(cleaned_results)}")
        
        return {
            'json_issues': json_issues,
            'backend_issues': backend_issues,
            'cleaned_files': list(cleaned_results.keys())
        }

def main():
    backend_path = "."  # Current directory (backend)
    cleaner = BackendCleaner(backend_path)
    report = cleaner.generate_cleanup_report()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Review cleaned JSON files (*_cleaned.json)")
    print("2. Remove redundant backend files if needed")
    print("3. Test the cleaned data with your application")
    
    return report

if __name__ == "__main__":
    main()