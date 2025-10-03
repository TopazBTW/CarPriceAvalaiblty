import csv
import random
import json

# Create comprehensive used cars data
used_cars_data = []

# Load brands from new cars
try:
    with open('data/json/morocco_cars_clean.json', 'r', encoding='utf-8') as f:
        new_cars = json.load(f)
    brands_models = {}
    for car in new_cars:
        brand = car['Brand']
        model = car['Model']
        if brand not in brands_models:
            brands_models[brand] = []
        if model not in brands_models[brand]:
            brands_models[brand].append(model)
    print(f"Loaded {len(brands_models)} brands from existing data")
except:
    brands_models = {
        'Toyota': ['Corolla', 'Camry', 'RAV4', 'Hilux', 'Yaris'],
        'Dacia': ['Logan', 'Sandero', 'Duster', 'Lodgy'],
        'Hyundai': ['i10', 'i20', 'Tucson', 'Elantra'],
        'Ford': ['Fiesta', 'Focus', 'Kuga', 'EcoSport'],
        'Volkswagen': ['Golf', 'Polo', 'Tiguan', 'Passat'],
        'Renault': ['Clio', 'Megane', 'Captur', 'Kadjar'],
        'Peugeot': ['208', '308', '2008', '3008'],
        'Citroen': ['C3', 'C4', 'C-Elysee'],
        'Nissan': ['Micra', 'Qashqai', 'X-Trail'],
        'Mercedes': ['A-Class', 'C-Class', 'E-Class', 'GLA'],
        'BMW': ['Serie 1', 'Serie 3', 'X1', 'X3'],
        'Audi': ['A3', 'A4', 'Q3', 'Q5']
    }
    print("Using fallback brand data")

locations = ['Casablanca', 'Rabat', 'Marrakech', 'Fes', 'Tangier', 'Agadir', 'Meknes', 'Oujda', 'Kenitra', 'Tetouan']
conditions = ['Excellent', 'Very Good', 'Good', 'Fair', 'Poor']
fuel_types = ['Gasoline', 'Diesel', 'Hybrid', 'Electric']
transmissions = ['Manual', 'Automatic', 'CVT']
seller_types = ['Dealer', 'Private', 'Showroom']

print('Generating 2500 used cars...')

for i in range(2500):
    brand = random.choice(list(brands_models.keys()))
    model = random.choice(brands_models[brand])
    year = random.randint(2010, 2024)
    
    # Calculate realistic KM and price
    age = 2025 - year
    km_driven = random.randint(age * 5000, age * 25000)
    
    # Base price calculation by brand tier
    if brand in ['Mercedes', 'BMW', 'Audi']:
        base_price = random.randint(200000, 800000)
    elif brand in ['Toyota', 'Volkswagen', 'Ford']:
        base_price = random.randint(80000, 300000)
    else:
        base_price = random.randint(50000, 200000)
    
    # Apply depreciation (15% per year + KM penalty)
    depreciation_rate = min(0.15 * age + (km_driven * 0.0001), 0.85)  # Max 85% depreciation
    price = max(int(base_price * (1 - depreciation_rate)), int(base_price * 0.15))
    
    used_car = {
        'Brand': brand,
        'Model': model,
        'Year': year,
        'Price': price,
        'KM_Driven': km_driven,
        'Fuel_Type': random.choice(fuel_types),
        'Transmission': random.choice(transmissions),
        'Condition': random.choice(conditions),
        'Location': random.choice(locations),
        'Seller_Type': random.choice(seller_types),
        'Phone': '+212' + str(random.randint(600000000, 699999999)),
        'Verified_Seller': random.choice([True, False]),
        'Days_Listed': random.randint(1, 180),
        'Views': random.randint(10, 500),
        'Source': random.choice(['Avito', 'Facebook Marketplace', 'Moteur.ma', 'Sarouty'])
    }
    
    used_cars_data.append(used_car)
    
    if (i + 1) % 500 == 0:
        print(f'Generated {i + 1} cars...')

# Save to CSV
columns = [
    'Brand', 'Model', 'Year', 'Price', 'KM_Driven', 'Fuel_Type', 
    'Transmission', 'Condition', 'Location', 'Seller_Type', 'Phone', 
    'Verified_Seller', 'Days_Listed', 'Views', 'Source'
]

with open('data/csv/morocco_used_cars.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=columns)
    writer.writeheader()
    writer.writerows(used_cars_data)

print(f'✅ Successfully created morocco_used_cars.csv with {len(used_cars_data)} entries')
print('\n📊 Sample entries:')
for i in range(5):
    car = used_cars_data[i]
    print(f'{i+1}. {car["Brand"]} {car["Model"]} {car["Year"]} - {car["Price"]:,} MAD - {car["KM_Driven"]:,} KM')
    print(f'   📍 {car["Location"]} | 🏷️ {car["Condition"]} | 🏪 {car["Seller_Type"]} | 🌐 {car["Source"]}')

# Statistics
total_cars = len(used_cars_data)
prices = [car['Price'] for car in used_cars_data]
print(f'\n📈 Dataset Statistics:')
print(f'Total cars: {total_cars:,}')
print(f'Price range: {min(prices):,} - {max(prices):,} MAD')
print(f'Average price: {sum(prices) // len(prices):,} MAD')

# Brand distribution
brands = {}
for car in used_cars_data:
    brand = car['Brand']
    brands[brand] = brands.get(brand, 0) + 1

print('\n🏷️ Top 5 brands:')
for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]:
    percentage = (count / total_cars) * 100
    print(f'  {brand}: {count} cars ({percentage:.1f}%)')

print('\n🎉 Used cars CSV generation complete!')