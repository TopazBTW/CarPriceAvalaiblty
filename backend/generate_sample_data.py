# Test sample CSV data for training
# You can use this as a template for your training data

import pandas as pd
import random
from datetime import datetime

# Generate sample data
brands = ['Toyota', 'Honda', 'Nissan', 'Hyundai', 'Kia', 'Ford', 'Volkswagen', 'Peugeot', 'Renault', 'Dacia']
toyota_models = ['Yaris', 'Corolla', 'Camry', 'RAV4', 'Prius', 'Hilux']
honda_models = ['Civic', 'Accord', 'CR-V', 'City', 'Jazz']
nissan_models = ['Micra', 'Sentra', 'Qashqai', 'X-Trail', 'Patrol']
other_models = ['Accent', 'Elantra', 'Tucson', 'Rio', 'Cerato', 'Focus', 'Fiesta', 'Golf', 'Polo', '208', '308', 'Clio', 'Logan']

fuel_types = ['Petrol', 'Diesel', 'CNG', 'Electric']
seller_types = ['Individual', 'Dealer']
transmissions = ['Manual', 'Automatic']
owners = ['First Owner', 'Second Owner', 'Third Owner', 'Fourth & Above Owner']

def generate_sample_data(n_samples=500):
    data = []
    current_year = datetime.now().year
    
    for _ in range(n_samples):
        brand = random.choice(brands)
        
        # Select model based on brand
        if brand == 'Toyota':
            model = random.choice(toyota_models)
        elif brand == 'Honda':
            model = random.choice(honda_models)
        elif brand == 'Nissan':
            model = random.choice(nissan_models)
        else:
            model = random.choice(other_models)
        
        year = random.randint(2010, current_year - 1)
        km_driven = random.randint(10000, 200000)
        fuel = random.choice(fuel_types)
        seller_type = random.choice(seller_types)
        transmission = random.choice(transmissions)
        owner = random.choice(owners)
        
        # Generate realistic price based on features
        base_price = {
            'Toyota': 120000,
            'Honda': 115000,
            'Nissan': 110000,
            'Hyundai': 95000,
            'Kia': 90000,
            'Ford': 85000,
            'Volkswagen': 100000,
            'Peugeot': 75000,
            'Renault': 70000,
            'Dacia': 60000
        }.get(brand, 80000)
        
        # Adjust for year (depreciation)
        age = current_year - year
        price = base_price * (0.85 ** (age / 3))  # 15% depreciation every 3 years
        
        # Adjust for mileage
        km_factor = max(0.5, 1 - (km_driven - 50000) / 500000)
        price *= km_factor
        
        # Adjust for fuel type
        if fuel == 'Diesel':
            price *= 1.1
        elif fuel == 'Electric':
            price *= 1.3
        elif fuel == 'CNG':
            price *= 0.9
        
        # Adjust for transmission
        if transmission == 'Automatic':
            price *= 1.15
        
        # Adjust for owner type
        owner_factor = {
            'First Owner': 1.0,
            'Second Owner': 0.85,
            'Third Owner': 0.7,
            'Fourth & Above Owner': 0.6
        }.get(owner, 0.8)
        price *= owner_factor
        
        # Add some random variation
        price *= random.uniform(0.8, 1.2)
        
        # Ensure reasonable price range
        price = max(15000, min(800000, int(price)))
        
        data.append({
            'Brand': brand,
            'Model': model,
            'Year': year,
            'KM_Driven': km_driven,
            'Fuel': fuel,
            'Seller_Type': seller_type,
            'Transmission': transmission,
            'Owner': owner,
            'Selling_Price': price
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Generate sample data
    df = generate_sample_data(500)
    
    # Save to CSV
    df.to_csv('sample_car_data.csv', index=False)
    print("Sample data generated and saved to 'sample_car_data.csv'")
    print(f"Generated {len(df)} samples")
    print("\nFirst 5 rows:")
    print(df.head())
    print(f"\nPrice range: {df['Selling_Price'].min():,} - {df['Selling_Price'].max():,} MAD")
    print(f"Average price: {df['Selling_Price'].mean():,.0f} MAD")