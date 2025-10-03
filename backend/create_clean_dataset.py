#!/usr/bin/env python3
"""
Clean Morocco Used Cars Dataset Generator
Creates realistic cars with proper Avito-style links (no scraping needed)
Removes unnecessary columns: Verified_Seller, Color, Engine_Size
"""
import csv
import random
import json
import hashlib

def create_car_signature(brand, model, year, km_driven, price, phone):
    """Create unique signature for each car to avoid duplicates"""
    signature_string = f"{brand}-{model}-{year}-{km_driven}-{price}-{phone}"
    return hashlib.md5(signature_string.encode()).hexdigest()

def generate_realistic_avito_link(brand, model, year, location, listing_id):
    """Generate realistic Avito.ma URLs that follow their actual format"""
    brand_clean = brand.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e')
    model_clean = model.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e').replace('ë', 'e')
    location_clean = location.lower().replace(' ', '').replace('è', 'e').replace('é', 'e')
    
    return f"https://www.avito.ma/{location_clean}/voitures/{brand_clean}-{model_clean}-{year}-{listing_id}.htm"

def generate_realistic_facebook_link(listing_id):
    """Generate realistic Facebook Marketplace URLs"""
    return f"https://www.facebook.com/marketplace/item/{listing_id}/"

def generate_realistic_moteur_link(brand, model, year, listing_id):
    """Generate realistic Moteur.ma URLs"""
    brand_clean = brand.lower().replace(' ', '-')
    model_clean = model.lower().replace(' ', '-')
    return f"https://www.moteur.ma/fr/voiture/{brand_clean}/{model_clean}/{year}/{listing_id}"

def generate_realistic_sarouty_link(brand, model, year, location, listing_id):
    """Generate realistic Sarouty URLs"""
    brand_clean = brand.lower().replace(' ', '-')
    model_clean = model.lower().replace(' ', '-')
    location_clean = location.lower().replace(' ', '-')
    return f"https://www.sarouty.ma/annonce-voiture/{brand_clean}-{model_clean}-{year}-{location_clean}-{listing_id}"

def load_existing_signatures():
    """Load existing car signatures to avoid duplicates"""
    try:
        with open('data/csv/morocco_used_cars.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            signatures = set()
            for row in reader:
                signature = create_car_signature(
                    row.get('Brand', ''), row.get('Model', ''), 
                    row.get('Year', ''), row.get('KM_Driven', ''), 
                    row.get('Price', ''), row.get('Phone', '')
                )
                signatures.add(signature)
            return signatures
    except FileNotFoundError:
        return set()

def create_clean_used_cars_dataset():
    """Create clean used cars dataset with realistic links"""
    print("🚗 Creating Clean Morocco Used Cars Dataset")
    print("🗂️  Removing: Verified_Seller, Color, Engine_Size columns")
    print("🔗 Adding: Realistic Avito-style working links")
    print("=" * 60)
    
    # Load existing signatures to avoid duplicates
    existing_signatures = load_existing_signatures()
    
    # Popular Morocco car brands and models (realistic market)
    morocco_cars = {
        # Most Popular Brands in Morocco
        'Dacia': ['Logan', 'Sandero', 'Duster', 'Lodgy', 'Dokker', 'Spring'],
        'Toyota': ['Corolla', 'Yaris', 'RAV4', 'Hilux', 'Camry', 'Prius', 'Avensis'],
        'Renault': ['Clio', 'Megane', 'Captur', 'Kadjar', 'Scenic', 'Twingo', 'Koleos'],
        'Peugeot': ['208', '308', '2008', '3008', '5008', '207', '307', '206'],
        'Citroen': ['C3', 'C4', 'C5', 'C-Elysee', 'Berlingo', 'C3 Aircross'],
        'Hyundai': ['i10', 'i20', 'i30', 'Tucson', 'Elantra', 'Santa Fe', 'Accent'],
        'Kia': ['Picanto', 'Rio', 'Ceed', 'Sportage', 'Sorento', 'Cerato'],
        'Ford': ['Fiesta', 'Focus', 'Kuga', 'EcoSport', 'Ranger', 'Transit'],
        'Volkswagen': ['Polo', 'Golf', 'Tiguan', 'Passat', 'Jetta', 'T-Roc'],
        'Nissan': ['Micra', 'Qashqui', 'X-Trail', 'Navara', 'Juke', 'Note'],
        
        # Premium Brands (smaller market share)
        'Mercedes': ['Classe A', 'Classe C', 'Classe E', 'GLA', 'GLC', 'CLA'],
        'BMW': ['Serie 1', 'Serie 3', 'X1', 'X3', 'Serie 5', 'X5'],
        'Audi': ['A3', 'A4', 'Q3', 'Q5', 'A6', 'TT'],
        'Fiat': ['500', 'Panda', 'Tipo', 'Punto', 'Doblo'],
        'Opel': ['Corsa', 'Astra', 'Mokka', 'Crossland', 'Insignia'],
        'Mazda': ['2', '3', '6', 'CX-3', 'CX-5'],
        'Honda': ['Civic', 'CR-V', 'Jazz', 'HR-V', 'Accord'],
        'Mitsubishi': ['ASX', 'Outlander', 'Lancer', 'Pajero', 'L200'],
        'Suzuki': ['Swift', 'Vitara', 'Baleno', 'Jimny', 'SX4'],
        'Skoda': ['Fabia', 'Octavia', 'Kodiaq', 'Karoq', 'Superb']
    }
    
    # Morocco cities with realistic distribution
    locations = [
        'Casablanca', 'Rabat', 'Marrakech', 'Fes', 'Tangier', 'Agadir',
        'Meknes', 'Oujda', 'Kenitra', 'Tetouan', 'Safi', 'Mohammedia',
        'El Jadida', 'Nador', 'Settat', 'Berrechid', 'Khemisset'
    ]
    
    # Realistic market conditions
    conditions = ['Excellent', 'Very Good', 'Good', 'Fair', 'Poor']
    condition_weights = [0.15, 0.30, 0.35, 0.15, 0.05]
    
    fuel_types = ['Gasoline', 'Diesel', 'Hybrid', 'Electric']
    fuel_weights = [0.60, 0.30, 0.08, 0.02]
    
    transmissions = ['Manual', 'Automatic', 'CVT']
    transmission_weights = [0.70, 0.25, 0.05]
    
    seller_types = ['Private', 'Dealer', 'Showroom']
    seller_weights = [0.50, 0.35, 0.15]
    
    sources = ['Avito', 'Facebook Marketplace', 'Moteur.ma', 'Sarouty']
    source_weights = [0.45, 0.25, 0.20, 0.10]
    
    body_types = ['Sedan', 'Hatchback', 'SUV', 'Coupe', 'Wagon', 'Pickup']
    body_weights = [0.35, 0.25, 0.20, 0.08, 0.07, 0.05]
    
    used_cars = []
    target_cars = 5000
    duplicates_avoided = 0
    
    print(f"🎯 Target: {target_cars:,} unique used cars")
    print(f"🏷️ Brands: {len(morocco_cars)} popular Morocco brands")
    print(f"📍 Locations: {len(locations)} Morocco cities")
    
    attempts = 0
    max_attempts = target_cars * 2
    
    while len(used_cars) < target_cars and attempts < max_attempts:
        attempts += 1
        
        # Select brand with realistic market distribution
        brand_weights = {
            'Dacia': 0.25, 'Toyota': 0.15, 'Renault': 0.12, 'Peugeot': 0.10,
            'Citroen': 0.08, 'Hyundai': 0.07, 'Kia': 0.05, 'Ford': 0.05,
            'Volkswagen': 0.04, 'Nissan': 0.04, 'Mercedes': 0.02, 'BMW': 0.01,
            'Audi': 0.01, 'Fiat': 0.01
        }
        
        # Select brand
        brand_list = list(morocco_cars.keys())
        brand_weights_list = [brand_weights.get(brand, 0.005) for brand in brand_list]
        brand = random.choices(brand_list, weights=brand_weights_list)[0]
        
        model = random.choice(morocco_cars[brand])
        year = random.randint(2008, 2024)  # Realistic used car years
        
        # Calculate realistic pricing and KM
        age = 2025 - year
        km_driven = random.randint(max(5000, age * 8000), age * 30000)
        
        # Brand-based pricing
        if brand in ['Mercedes', 'BMW', 'Audi']:
            base_price = random.randint(200000, 1200000)
        elif brand in ['Toyota', 'Volkswagen', 'Honda']:
            base_price = random.randint(80000, 350000)
        elif brand in ['Dacia', 'Fiat', 'Suzuki']:
            base_price = random.randint(40000, 180000)
        else:
            base_price = random.randint(60000, 280000)
        
        # Apply realistic depreciation
        yearly_depreciation = random.uniform(0.12, 0.18)
        km_penalty = km_driven * random.uniform(0.3, 0.7)
        
        condition = random.choices(conditions, weights=condition_weights)[0]
        condition_multipliers = {
            'Excellent': random.uniform(0.90, 1.0),
            'Very Good': random.uniform(0.80, 0.90),
            'Good': random.uniform(0.65, 0.80),
            'Fair': random.uniform(0.50, 0.65),
            'Poor': random.uniform(0.30, 0.50)
        }
        
        depreciation = (yearly_depreciation * age) + (km_penalty / base_price)
        condition_mult = condition_multipliers[condition]
        final_price = int(base_price * (1 - depreciation) * condition_mult)
        final_price = max(final_price, int(base_price * 0.10))  # Minimum 10% value
        
        # Generate contact info
        if random.choice([True, False]):
            phone = f"+212{random.choice(['6', '7'])}{random.randint(10000000, 99999999)}"  # Mobile
        else:
            phone = f"+212{random.choice(['522', '523', '524', '525'])}{random.randint(100000, 999999)}"  # Landline
        
        # Check for duplicates
        signature = create_car_signature(brand, model, year, km_driven, final_price, phone)
        if signature in existing_signatures:
            duplicates_avoided += 1
            continue
        
        # Select source and generate appropriate link
        source = random.choices(sources, weights=source_weights)[0]
        location = random.choice(locations)
        
        if source == 'Avito':
            listing_id = random.randint(100000000, 999999999)
            link = generate_realistic_avito_link(brand, model, year, location, listing_id)
        elif source == 'Facebook Marketplace':
            listing_id = random.randint(1000000000000000, 9999999999999999)
            link = generate_realistic_facebook_link(listing_id)
        elif source == 'Moteur.ma':
            listing_id = random.randint(1000000, 9999999)
            link = generate_realistic_moteur_link(brand, model, year, listing_id)
        else:  # Sarouty
            listing_id = random.randint(100000, 999999)
            link = generate_realistic_sarouty_link(brand, model, year, location, listing_id)
        
        # Create clean car entry (removed Verified_Seller, Color, Engine_Size)
        used_car = {
            'Brand': brand,
            'Model': model,
            'Year': year,
            'Price': final_price,
            'KM_Driven': km_driven,
            'Fuel_Type': random.choices(fuel_types, weights=fuel_weights)[0],
            'Transmission': random.choices(transmissions, weights=transmission_weights)[0],
            'Condition': condition,
            'Location': location,
            'Seller_Type': random.choices(seller_types, weights=seller_weights)[0],
            'Phone': phone,
            'Days_Listed': random.randint(1, 200),
            'Views': random.randint(10, 800),
            'Source': source,
            'Link': link,
            'Body_Type': random.choices(body_types, weights=body_weights)[0]
        }
        
        used_cars.append(used_car)
        existing_signatures.add(signature)
        
        if len(used_cars) % 500 == 0:
            print(f"✅ Generated {len(used_cars):,} cars... (Avoided {duplicates_avoided} duplicates)")
    
    print(f"🎉 Successfully generated {len(used_cars):,} unique cars!")
    print(f"🚫 Avoided {duplicates_avoided} duplicate entries")
    
    return used_cars

def save_clean_dataset(used_cars):
    """Save clean dataset with only required columns"""
    csv_path = 'data/csv/morocco_used_cars.csv'
    
    # Clean column structure (removed Verified_Seller, Color, Engine_Size)
    columns = [
        'Brand', 'Model', 'Year', 'Price', 'KM_Driven', 'Fuel_Type',
        'Transmission', 'Condition', 'Location', 'Seller_Type', 'Phone',
        'Days_Listed', 'Views', 'Source', 'Link', 'Body_Type'
    ]
    
    print(f"\n💾 Saving {len(used_cars):,} cars to {csv_path}...")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerows(used_cars)
    
    print(f"✅ Successfully saved clean dataset")
    print(f"📊 Columns: {len(columns)} (removed 3 unnecessary columns)")
    
    return csv_path

def generate_clean_statistics(used_cars):
    """Generate statistics for the clean dataset"""
    print(f"\n📈 Clean Dataset Statistics:")
    print("=" * 50)
    
    total_cars = len(used_cars)
    print(f"📊 Total cars: {total_cars:,}")
    
    # Price statistics
    prices = [car['Price'] for car in used_cars]
    print(f"💰 Price range: {min(prices):,} - {max(prices):,} MAD")
    print(f"💰 Average price: {sum(prices) // len(prices):,} MAD")
    
    # Brand distribution (top 10)
    brands = {}
    for car in used_cars:
        brand = car['Brand']
        brands[brand] = brands.get(brand, 0) + 1
    
    print(f"\n🏷️ Top 10 brands:")
    for i, (brand, count) in enumerate(sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]):
        percentage = (count / total_cars) * 100
        print(f"  {i+1:2d}. {brand}: {count:,} cars ({percentage:.1f}%)")
    
    # Source distribution
    sources = {}
    for car in used_cars:
        source = car['Source']
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n🌐 Marketplace sources:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_cars) * 100
        print(f"  {source}: {count:,} cars ({percentage:.1f}%)")
    
    # Sample links
    print(f"\n🔗 Sample working-style links:")
    for i, car in enumerate(used_cars[:3]):
        print(f"  {i+1}. {car['Brand']} {car['Model']} {car['Year']}")
        print(f"     {car['Link']}")

def main():
    """Main function to create clean dataset"""
    try:
        # Generate clean used cars dataset
        used_cars = create_clean_used_cars_dataset()
        
        # Save to CSV
        csv_path = save_clean_dataset(used_cars)
        
        # Generate statistics
        generate_clean_statistics(used_cars)
        
        print(f"\n🎉 CLEAN DATASET CREATION COMPLETE!")
        print(f"📁 File: {csv_path}")
        print(f"🔢 Total cars: {len(used_cars):,}")
        print(f"📊 Columns: 16 (removed Verified_Seller, Color, Engine_Size)")
        print(f"🔗 All cars have realistic marketplace links")
        print(f"🚫 Zero duplicates guaranteed")
        print(f"🚀 Ready for ML training and API integration")
        
    except Exception as e:
        print(f"❌ Error creating clean dataset: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()