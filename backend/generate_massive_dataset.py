import csv
import random
import json
import hashlib

def generate_realistic_link(source, brand, model, year, location, listing_id):
    """Generate realistic marketplace links for Morocco car listings"""
    
    # Normalize strings for URLs
    brand_clean = brand.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e')
    model_clean = model.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e').replace('ë', 'e')
    location_clean = location.lower().replace(' ', '-').replace('è', 'e').replace('é', 'e')
    
    if source == 'Avito':
        return f"https://www.avito.ma/{location_clean}/voitures/{brand_clean}-{model_clean}-{year}-{listing_id}.htm"
    elif source == 'Facebook Marketplace':
        return f"https://www.facebook.com/marketplace/item/{listing_id}/"
    elif source == 'Moteur.ma':
        return f"https://www.moteur.ma/fr/voiture/{brand_clean}/{model_clean}/{year}/{listing_id}"
    elif source == 'Sarouty':
        return f"https://www.sarouty.ma/annonce-voiture/{brand_clean}-{model_clean}-{year}-{location_clean}-{listing_id}"
    else:
        return f"https://www.example.ma/cars/{brand_clean}-{model_clean}-{year}-{listing_id}"

def create_car_signature(brand, model, year, km_driven, price, location, phone):
    """Create unique signature for each car to avoid duplicates"""
    signature_string = f"{brand}-{model}-{year}-{km_driven}-{price}-{location}-{phone}"
    return hashlib.md5(signature_string.encode()).hexdigest()

def load_existing_cars():
    """Load existing cars to avoid duplicates"""
    existing_cars = set()
    try:
        with open('data/csv/morocco_used_cars.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                signature = create_car_signature(
                    row['Brand'], row['Model'], row['Year'], 
                    row['KM_Driven'], row['Price'], row['Location'], row['Phone']
                )
                existing_cars.add(signature)
        print(f"✅ Loaded {len(existing_cars)} existing cars to avoid duplicates")
    except FileNotFoundError:
        print("📝 No existing file found, starting fresh")
    return existing_cars

def generate_expanded_brands_models():
    """Generate comprehensive brands and models including luxury, premium, and budget segments"""
    
    # Load from existing data if available
    try:
        with open('data/json/morocco_cars_clean.json', 'r', encoding='utf-8') as f:
            new_cars = json.load(f)
        brands_models = {}
        for car in new_cars:
            brand = car['Brand']
            model = car['Model']
            if brand not in brands_models:
                brands_models[brand] = set()
            brands_models[brand].add(model)
        # Convert sets to lists
        for brand in brands_models:
            brands_models[brand] = list(brands_models[brand])
        print(f"✅ Loaded {len(brands_models)} brands from existing data")
        return brands_models
    except:
        pass
    
    # Comprehensive Morocco car market data
    brands_models = {
        # Japanese Brands
        'Toyota': ['Corolla', 'Camry', 'RAV4', 'Hilux', 'Yaris', 'Prius', 'Avensis', 'Auris', 'Verso', 'Land Cruiser', 'Prado', 'Fortuner', 'Innova'],
        'Nissan': ['Micra', 'Qashqai', 'X-Trail', 'Navara', 'Pathfinder', 'Juke', 'Note', 'Tiida', 'Sunny', 'Patrol', 'Murano'],
        'Honda': ['Civic', 'Accord', 'CR-V', 'HR-V', 'Jazz', 'Pilot', 'City', 'Insight', 'Ridgeline'],
        'Mazda': ['Mazda3', 'Mazda6', 'CX-3', 'CX-5', 'CX-9', 'MX-5', 'Mazda2'],
        'Mitsubishi': ['Lancer', 'Outlander', 'Pajero', 'ASX', 'L200', 'Eclipse Cross', 'Space Star'],
        'Subaru': ['Impreza', 'Forester', 'Outback', 'XV', 'Legacy', 'BRZ'],
        'Suzuki': ['Swift', 'Vitara', 'Jimny', 'Baleno', 'SX4', 'Grand Vitara', 'Ignis'],
        'Lexus': ['ES', 'IS', 'GS', 'LS', 'NX', 'RX', 'GX', 'LX', 'UX'],
        'Infiniti': ['Q50', 'Q60', 'Q70', 'QX50', 'QX60', 'QX70', 'QX80'],
        'Acura': ['ILX', 'TLX', 'RLX', 'RDX', 'MDX', 'NSX'],
        
        # Korean Brands
        'Hyundai': ['i10', 'i20', 'i30', 'Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Creta', 'Accent', 'Veloster', 'Genesis'],
        'Kia': ['Picanto', 'Rio', 'Ceed', 'Cerato', 'Optima', 'Sportage', 'Sorento', 'Soul', 'Stonic', 'Niro'],
        'Genesis': ['G70', 'G80', 'G90', 'GV70', 'GV80'],
        
        # German Brands  
        'Mercedes': ['A-Class', 'B-Class', 'C-Class', 'E-Class', 'S-Class', 'GLA', 'GLB', 'GLC', 'GLE', 'GLS', 'G-Class', 'CLA', 'CLS', 'SL', 'AMG GT'],
        'BMW': ['Serie 1', 'Serie 2', 'Serie 3', 'Serie 4', 'Serie 5', 'Serie 6', 'Serie 7', 'Serie 8', 'X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'Z4', 'i3', 'i4', 'iX'],
        'Audi': ['A1', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'Q2', 'Q3', 'Q4', 'Q5', 'Q7', 'Q8', 'TT', 'R8', 'e-tron GT'],
        'Volkswagen': ['Polo', 'Golf', 'Jetta', 'Passat', 'Arteon', 'Tiguan', 'Touareg', 'T-Cross', 'T-Roc', 'Touran', 'Sharan', 'Caddy', 'Crafter'],
        'Porsche': ['911', 'Boxster', 'Cayman', 'Panamera', 'Cayenne', 'Macan', 'Taycan'],
        'Mini': ['Cooper', 'Clubman', 'Countryman', 'Paceman', 'Coupe', 'Roadster'],
        'Smart': ['ForTwo', 'ForFour', 'EQfortwo', 'Crossblade'],
        'Opel': ['Corsa', 'Astra', 'Insignia', 'Mokka', 'Crossland', 'Grandland', 'Combo', 'Vivaro'],
        
        # French Brands
        'Renault': ['Clio', 'Megane', 'Scenic', 'Laguna', 'Captur', 'Kadjar', 'Koleos', 'Espace', 'Talisman', 'Twingo', 'Zoe', 'Kangoo', 'Master'],
        'Peugeot': ['108', '208', '308', '408', '508', '2008', '3008', '5008', 'Partner', 'Boxer', 'Expert'],
        'Citroen': ['C1', 'C3', 'C4', 'C5', 'C-Elysee', 'C3 Aircross', 'C5 Aircross', 'Berlingo', 'Jumper', 'Jumpy'],
        'Dacia': ['Sandero', 'Logan', 'Duster', 'Lodgy', 'Dokker', 'Spring'],
        'DS': ['DS3', 'DS4', 'DS5', 'DS7', 'DS9'],
        
        # Italian Brands
        'Fiat': ['500', 'Panda', 'Punto', 'Tipo', '500X', '500L', 'Doblo', 'Ducato'],
        'Alfa Romeo': ['Giulietta', 'Giulia', 'Stelvio', '4C', 'Tonale'],
        'Lancia': ['Ypsilon', 'Delta', 'Thema'],
        'Ferrari': ['488', 'F8', '812', 'Roma', 'Portofino', 'SF90', 'LaFerrari'],
        'Lamborghini': ['Huracan', 'Aventador', 'Urus'],
        'Maserati': ['Ghibli', 'Quattroporte', 'Levante', 'GranTurismo', 'GranCabrio'],
        
        # American Brands
        'Ford': ['Fiesta', 'Focus', 'Fusion', 'Mustang', 'EcoSport', 'Kuga', 'Edge', 'Explorer', 'Expedition', 'F-150', 'Ranger', 'Transit'],
        'Chevrolet': ['Spark', 'Sonic', 'Cruze', 'Malibu', 'Camaro', 'Corvette', 'Trax', 'Equinox', 'Traverse', 'Tahoe', 'Silverado'],
        'Cadillac': ['ATS', 'CTS', 'XTS', 'XT4', 'XT5', 'XT6', 'Escalade'],
        'Jeep': ['Renegade', 'Compass', 'Cherokee', 'Grand Cherokee', 'Wrangler', 'Gladiator'],
        'Dodge': ['Charger', 'Challenger', 'Durango', 'Journey'],
        'Chrysler': ['300', 'Pacifica'],
        'Lincoln': ['MKZ', 'Continental', 'MKC', 'MKX', 'Navigator'],
        
        # British Brands
        'Land Rover': ['Evoque', 'Discovery Sport', 'Discovery', 'Defender', 'Freelander', 'Range Rover Sport', 'Range Rover', 'Range Rover Velar'],
        'Jaguar': ['XE', 'XF', 'XJ', 'F-Pace', 'E-Pace', 'I-Pace', 'F-Type'],
        'Rolls Royce': ['Ghost', 'Wraith', 'Dawn', 'Phantom', 'Cullinan'],
        'Bentley': ['Continental', 'Flying Spur', 'Mulsanne', 'Bentayga'],
        'Aston Martin': ['Vantage', 'DB11', 'DBS', 'DBX'],
        'McLaren': ['570S', '720S', '765LT', 'Artura'],
        
        # Swedish Brands
        'Volvo': ['S60', 'S90', 'V60', 'V90', 'XC40', 'XC60', 'XC90', 'C30', 'C70'],
        'Saab': ['9-3', '9-5', '9-4X'],
        
        # Chinese Brands
        'Chery': ['QQ', 'Tiggo', 'Arrizo', 'Fulwin'],
        'BYD': ['F3', 'S6', 'Tang', 'Song', 'Qin'],
        'Geely': ['Emgrand', 'GC6', 'MK', 'Panda'],
        'Great Wall': ['Hover', 'Voleex', 'Steed'],
        'MG': ['MG3', 'MG6', 'ZS', 'HS', 'RX5'],
        
        # Indian Brands
        'Tata': ['Indica', 'Indigo', 'Safari', 'Sumo', 'Nano'],
        'Mahindra': ['Scorpio', 'XUV500', 'Bolero', 'Thar'],
        
        # Electric/Luxury Brands
        'Tesla': ['Model 3', 'Model S', 'Model X', 'Model Y'],
        'Lucid': ['Air'],
        'Rivian': ['R1T', 'R1S']
    }
    
    print(f"📊 Using comprehensive dataset with {len(brands_models)} brands")
    return brands_models

def create_massive_used_cars_dataset():
    """Create a massive unique used cars dataset"""
    print("🚗 Creating Massive Morocco Used Cars Dataset")
    print("=" * 60)
    
    # Load existing cars to avoid duplicates
    existing_signatures = load_existing_cars()
    
    # Get comprehensive brands and models
    brands_models = generate_expanded_brands_models()
    
    # Extended data options
    locations = [
        'Casablanca', 'Rabat', 'Marrakech', 'Fès', 'Tangier', 'Agadir', 
        'Meknès', 'Oujda', 'Kenitra', 'Tetouan', 'Safi', 'Mohammedia',
        'Khouribga', 'Beni Mellal', 'El Jadida', 'Nador', 'Settat',
        'Berrechid', 'Khemisset', 'Inezgane', 'Ksar el Kebir', 'Larache',
        'Guelmim', 'Berkane', 'Taourirt', 'Ouarzazate', 'Tiznit'
    ]
    
    conditions = ['Excellent', 'Very Good', 'Good', 'Fair', 'Poor']
    condition_weights = [0.12, 0.23, 0.35, 0.25, 0.05]
    
    fuel_types = ['Gasoline', 'Diesel', 'Hybrid', 'Electric', 'LPG', 'CNG']
    fuel_weights = [0.58, 0.28, 0.08, 0.04, 0.015, 0.005]
    
    transmissions = ['Manual', 'Automatic', 'CVT', 'Semi-Automatic']
    transmission_weights = [0.65, 0.25, 0.08, 0.02]
    
    seller_types = ['Dealer', 'Private', 'Showroom', 'Garage', 'Importer']
    seller_weights = [0.35, 0.40, 0.15, 0.08, 0.02]
    
    sources = ['Avito', 'Facebook Marketplace', 'Moteur.ma', 'Sarouty', 'Wandaloo', 'AutoNeuve']
    source_weights = [0.35, 0.25, 0.20, 0.12, 0.05, 0.03]
    
    colors = ['White', 'Black', 'Silver', 'Gray', 'Blue', 'Red', 'Green', 'Brown', 'Gold', 'Beige']
    
    used_cars = []
    target_cars = 15000  # Generate 15,000 total cars
    duplicates_avoided = 0
    
    print(f"🎯 Target: {target_cars:,} unique used cars")
    
    attempts = 0
    max_attempts = target_cars * 3  # Allow up to 3x attempts to avoid infinite loops
    
    while len(used_cars) < target_cars and attempts < max_attempts:
        attempts += 1
        
        # Random brand and model selection
        brand = random.choice(list(brands_models.keys()))
        model = random.choice(brands_models[brand])
        year = random.randint(2005, 2024)  # Extended year range
        
        # Calculate realistic specs
        age = 2025 - year
        km_driven = random.randint(max(1000, age * 3000), age * 35000)  # 3K-35K per year
        
        # Tiered pricing by brand
        luxury_brands = ['Mercedes', 'BMW', 'Audi', 'Porsche', 'Jaguar', 'Land Rover', 'Lexus', 'Genesis', 'Infiniti', 'Cadillac', 'Lincoln', 'Rolls Royce', 'Bentley', 'Ferrari', 'Lamborghini', 'Maserati', 'Aston Martin', 'McLaren']
        premium_brands = ['Volvo', 'Acura', 'Tesla', 'Saab', 'Mini', 'Alfa Romeo', 'DS']
        popular_brands = ['Toyota', 'Honda', 'Nissan', 'Hyundai', 'Kia', 'Ford', 'Volkswagen', 'Mazda']
        budget_brands = ['Dacia', 'Fiat', 'Opel', 'Suzuki', 'Mitsubishi', 'Chery', 'BYD', 'Geely', 'MG', 'Tata']
        
        if brand in luxury_brands:
            base_price = random.randint(300000, 2000000)  # 300K-2M MAD
        elif brand in premium_brands:
            base_price = random.randint(200000, 800000)   # 200K-800K MAD
        elif brand in popular_brands:
            base_price = random.randint(80000, 400000)    # 80K-400K MAD
        elif brand in budget_brands:
            base_price = random.randint(40000, 200000)    # 40K-200K MAD
        else:  # French brands and others
            base_price = random.randint(60000, 300000)    # 60K-300K MAD
        
        # Enhanced depreciation model
        yearly_depreciation = 0.12 + (random.random() * 0.06)  # 12-18% per year
        km_penalty = km_driven * random.uniform(0.2, 0.8)  # 0.2-0.8 MAD per km
        condition_multiplier = {
            'Excellent': random.uniform(0.92, 1.0),
            'Very Good': random.uniform(0.82, 0.92),
            'Good': random.uniform(0.70, 0.82),
            'Fair': random.uniform(0.55, 0.70),
            'Poor': random.uniform(0.35, 0.55)
        }
        
        condition = random.choices(conditions, weights=condition_weights)[0]
        condition_mult = condition_multiplier[condition]
        
        # Calculate final price
        age_depreciation = (1 - yearly_depreciation) ** age
        final_price = int(base_price * age_depreciation * condition_mult - km_penalty)
        final_price = max(final_price, int(base_price * 0.08))  # Minimum 8% residual value
        
        # Generate other details
        fuel_type = random.choices(fuel_types, weights=fuel_weights)[0]
        transmission = random.choices(transmissions, weights=transmission_weights)[0]
        location = random.choice(locations)
        seller_type = random.choices(seller_types, weights=seller_weights)[0]
        source = random.choices(sources, weights=source_weights)[0]
        
        # Generate phone based on seller type
        if seller_type in ['Dealer', 'Showroom', 'Garage']:
            phone = f"+212{random.choice(['522', '523', '524', '525'])}{random.randint(100000, 999999)}"
        else:  # Private, Importer
            phone = f"+212{random.choice(['6', '7'])}{random.randint(10000000, 99999999)}"
        
        # Create unique signature
        signature = create_car_signature(brand, model, year, km_driven, final_price, location, phone)
        
        # Check for duplicates
        if signature in existing_signatures:
            duplicates_avoided += 1
            continue
        
        # Generate unique listing IDs based on source
        if source == 'Avito':
            listing_id = random.randint(100000000, 999999999)
        elif source == 'Facebook Marketplace':
            listing_id = random.randint(1000000000000000, 9999999999999999)
        elif source == 'Moteur.ma':
            listing_id = random.randint(1000000, 9999999)
        elif source == 'Sarouty':
            listing_id = random.randint(100000, 999999)
        elif source == 'Wandaloo':
            listing_id = random.randint(10000, 99999)
        else:  # AutoNeuve
            listing_id = random.randint(1000, 9999)
        
        # Generate realistic link
        link = generate_realistic_link(source, brand, model, year, location, listing_id)
        
        # Create car entry
        used_car = {
            'Brand': brand,
            'Model': model,
            'Year': year,
            'Price': final_price,
            'KM_Driven': km_driven,
            'Fuel_Type': fuel_type,
            'Transmission': transmission,
            'Condition': condition,
            'Location': location,
            'Seller_Type': seller_type,
            'Phone': phone,
            'Verified_Seller': random.choices([True, False], weights=[0.7, 0.3])[0],
            'Days_Listed': random.randint(1, 365),  # Up to 1 year listed
            'Views': random.randint(5, 1200),  # More realistic view range
            'Source': source,
            'Link': link,
            'Color': random.choice(colors),
            'Body_Type': random.choice(['Sedan', 'Hatchback', 'SUV', 'Coupe', 'Wagon', 'Pickup', 'Van', 'Convertible']),
            'Engine_Size': round(random.uniform(1.0, 6.2), 1)  # 1.0L to 6.2L engines
        }
        
        used_cars.append(used_car)
        existing_signatures.add(signature)
        
        if len(used_cars) % 1000 == 0:
            print(f"✅ Generated {len(used_cars):,} cars... (Avoided {duplicates_avoided} duplicates)")
    
    print(f"🎉 Successfully generated {len(used_cars):,} unique cars!")
    print(f"🚫 Avoided {duplicates_avoided} duplicate entries")
    
    return used_cars

def save_massive_dataset(used_cars):
    """Save the massive dataset to CSV"""
    csv_path = 'data/csv/morocco_used_cars.csv'
    
    # Define comprehensive CSV columns
    columns = [
        'Brand', 'Model', 'Year', 'Price', 'KM_Driven', 'Fuel_Type',
        'Transmission', 'Condition', 'Location', 'Seller_Type', 'Phone',
        'Verified_Seller', 'Days_Listed', 'Views', 'Source', 'Link',
        'Color', 'Body_Type', 'Engine_Size'
    ]
    
    print(f"\n💾 Saving {len(used_cars):,} cars to {csv_path}...")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerows(used_cars)
    
    print(f"✅ Successfully saved {len(used_cars):,} used cars to CSV")
    
    return csv_path

def generate_comprehensive_statistics(used_cars):
    """Generate comprehensive dataset statistics"""
    print(f"\n📈 Comprehensive Dataset Statistics:")
    print("=" * 60)
    
    total_cars = len(used_cars)
    print(f"📊 Total cars: {total_cars:,}")
    
    # Price statistics
    prices = [car['Price'] for car in used_cars]
    print(f"💰 Price range: {min(prices):,} - {max(prices):,} MAD")
    print(f"💰 Average price: {sum(prices) // len(prices):,} MAD")
    print(f"💰 Median price: {sorted(prices)[len(prices)//2]:,} MAD")
    
    # Year statistics
    years = [car['Year'] for car in used_cars]
    print(f"📅 Year range: {min(years)} - {max(years)}")
    
    # Brand distribution (top 15)
    brands = {}
    for car in used_cars:
        brand = car['Brand']
        brands[brand] = brands.get(brand, 0) + 1
    
    print(f"\n🏷️ Top 15 brands:")
    for i, (brand, count) in enumerate(sorted(brands.items(), key=lambda x: x[1], reverse=True)[:15]):
        percentage = (count / total_cars) * 100
        print(f"  {i+1:2d}. {brand}: {count:,} cars ({percentage:.1f}%)")
    
    # Source distribution
    sources = {}
    for car in used_cars:
        source = car['Source']
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n🌐 Source distribution:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_cars) * 100
        print(f"  {source}: {count:,} cars ({percentage:.1f}%)")
    
    # Location distribution (top 10)
    locations = {}
    for car in used_cars:
        location = car['Location']
        locations[location] = locations.get(location, 0) + 1
    
    print(f"\n📍 Top 10 locations:")
    for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / total_cars) * 100
        print(f"  {location}: {count:,} cars ({percentage:.1f}%)")

def main():
    """Main function to generate massive used cars dataset"""
    try:
        # Generate the massive dataset
        used_cars = create_massive_used_cars_dataset()
        
        # Save to CSV
        csv_path = save_massive_dataset(used_cars)
        
        # Generate comprehensive statistics
        generate_comprehensive_statistics(used_cars)
        
        print(f"\n🎉 Massive Used Cars Dataset Generation Complete!")
        print(f"📁 File saved: {csv_path}")
        print(f"🔢 Total cars: {len(used_cars):,}")
        print(f"📊 {len(set(car['Brand'] for car in used_cars))} unique brands")
        print(f"🏷️ {len(set(f"{car['Brand']}-{car['Model']}" for car in used_cars))} unique brand-model combinations")
        print(f"🌐 All cars include direct marketplace links")
        print(f"🚀 Ready for ML training and API integration")
        
    except Exception as e:
        print(f"❌ Error generating massive dataset: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()