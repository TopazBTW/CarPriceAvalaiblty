#!/usr/bin/env python3
"""
Morocco Car Market Data Generator
Generate 10,000 realistic car listings based on actual Morocco market data
"""
import csv
import random
from datetime import datetime, timedelta
import os

class MoroccoMarketDataGenerator:
    def __init__(self):
        # Real Morocco car market data (2025)
        self.market_data = {
            'Dacia': {
                'models': {
                    'Logan': {'base_price': 140000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline'], 'popularity': 0.25},
                    'Sandero': {'base_price': 130000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline'], 'popularity': 0.20},
                    'Duster': {'base_price': 180000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.30},
                    'Lodgy': {'base_price': 160000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.15},
                    'Dokker': {'base_price': 145000, 'years': [2018, 2019, 2020, 2021, 2022], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.10}
                },
                'market_share': 0.35
            },
            'Renault': {
                'models': {
                    'Clio': {'base_price': 150000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.30},
                    'Megane': {'base_price': 200000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.20},
                    'Captur': {'base_price': 220000, 'years': [2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.25},
                    'Kadjar': {'base_price': 280000, 'years': [2018, 2019, 2020, 2021, 2022], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.15},
                    'Talisman': {'base_price': 320000, 'years': [2018, 2019, 2020, 2021], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.10}
                },
                'market_share': 0.15
            },
            'Peugeot': {
                'models': {
                    '208': {'base_price': 160000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.25},
                    '308': {'base_price': 210000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.20},
                    '2008': {'base_price': 230000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.30},
                    '3008': {'base_price': 320000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel', 'Hybrid'], 'popularity': 0.20},
                    '5008': {'base_price': 380000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.05}
                },
                'market_share': 0.12
            },
            'Toyota': {
                'models': {
                    'Yaris': {'base_price': 170000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Hybrid'], 'popularity': 0.20},
                    'Corolla': {'base_price': 220000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Hybrid'], 'popularity': 0.25},
                    'RAV4': {'base_price': 380000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Hybrid'], 'popularity': 0.20},
                    'Hilux': {'base_price': 420000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Diesel'], 'popularity': 0.25},
                    'Land Cruiser': {'base_price': 850000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Diesel'], 'popularity': 0.10}
                },
                'market_share': 0.08
            },
            'Hyundai': {
                'models': {
                    'i10': {'base_price': 130000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline'], 'popularity': 0.20},
                    'i20': {'base_price': 155000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline'], 'popularity': 0.25},
                    'Accent': {'base_price': 180000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline'], 'popularity': 0.20},
                    'Tucson': {'base_price': 320000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel', 'Hybrid'], 'popularity': 0.25},
                    'Santa Fe': {'base_price': 450000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.10}
                },
                'market_share': 0.07
            },
            'Volkswagen': {
                'models': {
                    'Polo': {'base_price': 165000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.25},
                    'Golf': {'base_price': 230000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.25},
                    'Tiguan': {'base_price': 380000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.30},
                    'Passat': {'base_price': 340000, 'years': [2018, 2019, 2020, 2021, 2022], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.15},
                    'Touareg': {'base_price': 720000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.05}
                },
                'market_share': 0.06
            },
            'Ford': {
                'models': {
                    'Fiesta': {'base_price': 150000, 'years': [2018, 2019, 2020, 2021, 2022], 'fuel': ['Gasoline'], 'popularity': 0.20},
                    'Focus': {'base_price': 200000, 'years': [2018, 2019, 2020, 2021, 2022], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.20},
                    'Kuga': {'base_price': 320000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel', 'Hybrid'], 'popularity': 0.30},
                    'Mustang': {'base_price': 650000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline'], 'popularity': 0.10},
                    'Ranger': {'base_price': 380000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Diesel'], 'popularity': 0.20}
                },
                'market_share': 0.04
            },
            'Nissan': {
                'models': {
                    'Micra': {'base_price': 140000, 'years': [2018, 2019, 2020, 2021, 2022], 'fuel': ['Gasoline'], 'popularity': 0.15},
                    'Juke': {'base_price': 250000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline'], 'popularity': 0.25},
                    'Qashqai': {'base_price': 290000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.35},
                    'X-Trail': {'base_price': 380000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.20},
                    'Patrol': {'base_price': 750000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Diesel'], 'popularity': 0.05}
                },
                'market_share': 0.05
            },
            'Citroen': {
                'models': {
                    'C3': {'base_price': 155000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.30},
                    'C4': {'base_price': 210000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.25},
                    'C5 Aircross': {'base_price': 310000, 'years': [2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel', 'Hybrid'], 'popularity': 0.25},
                    'Berlingo': {'base_price': 180000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.15},
                    'Jumper': {'base_price': 280000, 'years': [2018, 2019, 2020, 2021, 2022], 'fuel': ['Diesel'], 'popularity': 0.05}
                },
                'market_share': 0.04
            },
            'Kia': {
                'models': {
                    'Picanto': {'base_price': 125000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline'], 'popularity': 0.20},
                    'Rio': {'base_price': 150000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline'], 'popularity': 0.20},
                    'Sportage': {'base_price': 310000, 'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024], 'fuel': ['Gasoline', 'Diesel', 'Hybrid'], 'popularity': 0.40},
                    'Sorento': {'base_price': 420000, 'years': [2018, 2019, 2020, 2021, 2022, 2023], 'fuel': ['Gasoline', 'Diesel'], 'popularity': 0.15},
                    'Stinger': {'base_price': 520000, 'years': [2018, 2019, 2020, 2021, 2022], 'fuel': ['Gasoline'], 'popularity': 0.05}
                },
                'market_share': 0.04
            }
        }
        
        self.morocco_cities = {
            'Casablanca': 0.25,
            'Rabat': 0.15,
            'Marrakech': 0.12,
            'Fes': 0.10,
            'Tangier': 0.10,
            'Agadir': 0.08,
            'Meknes': 0.06,
            'Oujda': 0.05,
            'Kenitra': 0.05,
            'Tetouan': 0.04
        }
        
        self.transmission_rates = {
            'Manual': 0.65,
            'Automatic': 0.35
        }
        
        self.condition_rates = {
            'Excellent': 0.15,
            'Very Good': 0.35,
            'Good': 0.40,
            'Fair': 0.10
        }
        
        self.seller_types = {
            'Private': 0.70,
            'Dealer': 0.30
        }
        
        self.body_types = {
            'Sedan': 0.30,
            'Hatchback': 0.25,
            'SUV': 0.25,
            'Pickup': 0.10,
            'Coupe': 0.05,
            'Van': 0.05
        }

    def weighted_choice(self, choices_dict):
        """Make weighted random choice"""
        choices = list(choices_dict.keys())
        weights = list(choices_dict.values())
        return random.choices(choices, weights=weights)[0]

    def calculate_depreciation(self, base_price, year, condition, km_driven):
        """Calculate realistic depreciation"""
        current_year = 2025
        age = current_year - year
        
        # Age depreciation (15% first year, then 10% per year)
        if age == 0:
            age_factor = 0.95
        elif age == 1:
            age_factor = 0.85
        else:
            age_factor = 0.85 * (0.90 ** (age - 1))
        
        # Kilometer depreciation
        if km_driven < 30000:
            km_factor = 1.0
        elif km_driven < 80000:
            km_factor = 0.95
        elif km_driven < 150000:
            km_factor = 0.85
        else:
            km_factor = 0.75
        
        # Condition factor
        condition_factors = {
            'Excellent': 1.1,
            'Very Good': 1.0,
            'Good': 0.90,
            'Fair': 0.75
        }
        condition_factor = condition_factors[condition]
        
        # Calculate final price
        price = base_price * age_factor * km_factor * condition_factor
        
        # Add random variation (±5%)
        variation = random.uniform(0.95, 1.05)
        price = int(price * variation)
        
        return price

    def generate_kilometers(self, year):
        """Generate realistic kilometers based on year"""
        current_year = 2025
        age = current_year - year
        
        if age == 0:
            return random.randint(1000, 15000)
        else:
            # Average 15,000-20,000 km per year
            avg_km = random.randint(15000, 20000) * age
            # Add variation
            variation = random.uniform(0.7, 1.3)
            km = int(avg_km * variation)
            # Cap at reasonable maximum
            return min(km, 300000)

    def generate_phone(self):
        """Generate realistic Morocco phone number"""
        prefix = random.choice([6, 7])  # Mobile prefixes in Morocco
        number = random.randint(10000000, 99999999)
        return f"+212{prefix}{number}"

    def generate_car(self):
        """Generate one realistic car listing"""
        # Select brand based on market share
        brand = self.weighted_choice({b: d['market_share'] for b, d in self.market_data.items()})
        brand_data = self.market_data[brand]
        
        # Select model based on popularity
        model = self.weighted_choice({m: d['popularity'] for m, d in brand_data['models'].items()})
        model_data = brand_data['models'][model]
        
        # Select year from available years
        year = random.choice(model_data['years'])
        
        # Generate kilometers
        km_driven = self.generate_kilometers(year)
        
        # Select fuel type
        fuel_type = random.choice(model_data['fuel'])
        
        # Select transmission based on rates
        transmission = self.weighted_choice(self.transmission_rates)
        
        # Select condition
        condition = self.weighted_choice(self.condition_rates)
        
        # Calculate price
        price = self.calculate_depreciation(model_data['base_price'], year, condition, km_driven)
        
        # Select location
        location = self.weighted_choice(self.morocco_cities)
        
        # Select seller type
        seller_type = self.weighted_choice(self.seller_types)
        
        # Generate phone
        phone = self.generate_phone()
        
        # Days listed (1-180 days)
        days_listed = random.randint(1, 180)
        
        # Views (more for newer/cheaper cars)
        base_views = random.randint(50, 500)
        if year >= 2023:
            base_views = int(base_views * 1.5)
        if price < 150000:
            base_views = int(base_views * 1.3)
        views = min(base_views, 2000)
        
        # Body type
        body_type = self.weighted_choice(self.body_types)
        
        return {
            'Brand': brand,
            'Model': model,
            'Year': year,
            'Price': price,
            'KM_Driven': km_driven,
            'Fuel_Type': fuel_type,
            'Transmission': transmission,
            'Condition': condition,
            'Location': location,
            'Seller_Type': seller_type,
            'Phone': phone,
            'Days_Listed': days_listed,
            'Views': views,
            'Body_Type': body_type
        }

    def generate_dataset(self, num_cars=10000):
        """Generate complete dataset"""
        print(f"🇲🇦 Génération de {num_cars:,} voitures du marché marocain...")
        print("=" * 60)
        
        cars = []
        for i in range(num_cars):
            car = self.generate_car()
            cars.append(car)
            
            if (i + 1) % 1000 == 0:
                print(f"   Généré: {i + 1:,}/{num_cars:,} voitures ({(i+1)/num_cars*100:.1f}%)")
        
        print(f"✅ Génération terminée: {num_cars:,} voitures")
        return cars

    def save_dataset(self, cars, filename='data/csv/morocco_used_cars.csv'):
        """Save dataset to CSV"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        fieldnames = [
            'Brand', 'Model', 'Year', 'Price', 'KM_Driven', 'Fuel_Type',
            'Transmission', 'Condition', 'Location', 'Seller_Type', 'Phone',
            'Days_Listed', 'Views', 'Body_Type'
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(cars)
            
            print(f"✅ Sauvegardé dans: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False

    def show_statistics(self, cars):
        """Show dataset statistics"""
        print("\n📊 STATISTIQUES DU DATASET")
        print("=" * 60)
        
        # Brand distribution
        brands = {}
        for car in cars:
            brands[car['Brand']] = brands.get(car['Brand'], 0) + 1
        
        print("\n🚗 Distribution des marques:")
        for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
            pct = count / len(cars) * 100
            print(f"   {brand:15s}: {count:5,} ({pct:5.2f}%)")
        
        # Price statistics
        prices = [car['Price'] for car in cars]
        print(f"\n💰 Prix (MAD):")
        print(f"   Minimum:  {min(prices):10,}")
        print(f"   Maximum:  {max(prices):10,}")
        print(f"   Moyenne:  {sum(prices)//len(prices):10,}")
        print(f"   Médiane:  {sorted(prices)[len(prices)//2]:10,}")
        
        # Year distribution
        years = {}
        for car in cars:
            years[car['Year']] = years.get(car['Year'], 0) + 1
        
        print(f"\n📅 Distribution des années:")
        for year in sorted(years.keys(), reverse=True):
            count = years[year]
            pct = count / len(cars) * 100
            print(f"   {year}: {count:5,} ({pct:5.2f}%)")
        
        # Location distribution
        locations = {}
        for car in cars:
            locations[car['Location']] = locations.get(car['Location'], 0) + 1
        
        print(f"\n📍 Top 5 Villes:")
        for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
            pct = count / len(cars) * 100
            print(f"   {loc:15s}: {count:5,} ({pct:5.2f}%)")
        
        # Sample cars
        print(f"\n📋 Exemples de voitures:")
        for i, car in enumerate(random.sample(cars, min(10, len(cars))), 1):
            print(f"   {i:2d}. {car['Year']} {car['Brand']} {car['Model']:12s} - {car['Price']:7,} MAD")
            print(f"       {car['KM_Driven']:6,} km | {car['Fuel_Type']:8s} | {car['Transmission']:9s} | {car['Location']}")

def main():
    """Main function"""
    try:
        generator = MoroccoMarketDataGenerator()
        
        # Generate 10,000 cars
        cars = generator.generate_dataset(10000)
        
        # Save dataset
        if generator.save_dataset(cars):
            # Show statistics
            generator.show_statistics(cars)
            
            print(f"\n🎉 SUCCÈS COMPLET!")
            print(f"   📁 Fichier: data/csv/morocco_used_cars.csv")
            print(f"   📊 Total: {len(cars):,} voitures")
            print(f"   ✅ Données basées sur le marché réel marocain 2025")
            
        else:
            print("❌ Échec de la sauvegarde")
            
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")

if __name__ == "__main__":
    main()
