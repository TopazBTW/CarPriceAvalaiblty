import asyncio
import aiohttp
import json
import os

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_CSV_FILE = "sample_car_data.csv"

async def test_api():
    """Test all API endpoints"""
    
    async with aiohttp.ClientSession() as session:
        print("🚀 Testing Morocco Car Price Prediction API\n")
        
        # Test 1: Health Check
        print("1️⃣  Testing health endpoint...")
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"   ✅ Health check passed")
                    print(f"   📊 Status: {health_data['status']}")
                    print(f"   🤖 Model loaded: {health_data['model_loaded']}")
                    print(f"   🕸️  Scraping enabled: {health_data['scraping_enabled']}")
                else:
                    print(f"   ❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
        
        print()
        
        # Test 2: Upload CSV (if file exists)
        if os.path.exists(TEST_CSV_FILE):
            print("2️⃣  Testing CSV upload...")
            try:
                with open(TEST_CSV_FILE, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f, filename=TEST_CSV_FILE, content_type='text/csv')
                    
                    async with session.post(f"{BASE_URL}/upload-csv", data=data) as response:
                        if response.status == 200:
                            upload_result = await response.json()
                            print(f"   ✅ CSV upload successful")
                            print(f"   🎯 Accuracy: {upload_result.get('accuracy', 0):.1f}%")
                            print(f"   📈 Training samples: {upload_result.get('training_samples', 0)}")
                        else:
                            error_text = await response.text()
                            print(f"   ❌ CSV upload failed: {response.status}")
                            print(f"   📝 Error: {error_text}")
            except Exception as e:
                print(f"   ❌ CSV upload error: {e}")
        else:
            print("2️⃣  Skipping CSV upload (no sample file found)")
        
        print()
        
        # Test 3: Prediction
        print("3️⃣  Testing prediction endpoint...")
        test_car = {
            "Brand": "Toyota",
            "Model": "Yaris",
            "Year": 2018,
            "KM_Driven": 80000,
            "Fuel": "Petrol",
            "Seller_Type": "Individual",
            "Transmission": "Manual",
            "Owner": "First Owner"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/predict", 
                json=test_car,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    prediction = await response.json()
                    print(f"   ✅ Prediction successful")
                    print(f"   💰 Predicted price: {prediction['predicted_price']:,} {prediction['currency']}")
                    
                    if prediction.get('market_avg_price'):
                        print(f"   📊 Market average: {prediction['market_avg_price']:,} {prediction['currency']}")
                    
                    print(f"   🎯 Model confidence: {prediction['model_confidence']:.1%}")
                    print(f"   🕸️  Scraping source: {prediction['scraping_source']}")
                    
                    if prediction.get('listings'):
                        print(f"   📋 Found {len(prediction['listings'])} market listings:")
                        for i, listing in enumerate(prediction['listings'][:3], 1):
                            print(f"      {i}. {listing['title']} - {listing['price']:,} MAD")
                    else:
                        print(f"   📋 No market listings found")
                        
                else:
                    error_text = await response.text()
                    print(f"   ❌ Prediction failed: {response.status}")
                    print(f"   📝 Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Prediction error: {e}")
        
        print()
        
        # Test 4: Scraping (standalone test)
        print("4️⃣  Testing scraping functions...")
        try:
            from scrapers import fetch_avito_listings, compute_average_price
            
            print("   🔍 Testing Avito scraping...")
            avito_results = await fetch_avito_listings("Toyota", "Yaris", 2018)
            
            if avito_results:
                print(f"   ✅ Avito scraping successful: {len(avito_results)} results")
                avg_price = compute_average_price(avito_results)
                if avg_price:
                    print(f"   💰 Average price from listings: {avg_price:,} MAD")
                
                # Show first few results
                for i, result in enumerate(avito_results[:2], 1):
                    print(f"      {i}. {result['title']} - {result['price']:,} MAD")
            else:
                print("   ⚠️  No results from Avito (this is normal if rate-limited)")
                
        except Exception as e:
            print(f"   ⚠️  Scraping test error: {e}")
        
        print("\n" + "="*50)
        print("🎉 API Testing Complete!")
        print("="*50)

def test_model_locally():
    """Test ML model functionality locally"""
    print("🧠 Testing ML Model locally...\n")
    
    try:
        from ml_model import MLModel
        import pandas as pd
        
        # Test model loading
        model = MLModel()
        print(f"Model loaded: {model.is_loaded()}")
        
        # If we have sample data, test training
        if os.path.exists(TEST_CSV_FILE):
            print("📚 Testing model training...")
            df = pd.read_csv(TEST_CSV_FILE)
            accuracy = model.train(df)
            print(f"✅ Training completed with {accuracy:.1f}% accuracy")
            
            # Test prediction
            print("🔮 Testing model prediction...")
            test_input = {
                "Brand": "Toyota",
                "Model": "Yaris", 
                "Year": 2018,
                "KM_Driven": 80000,
                "Fuel": "Petrol",
                "Seller_Type": "Individual",
                "Transmission": "Manual",
                "Owner": "First Owner"
            }
            
            result = model.predict(test_input)
            print(f"✅ Prediction: {result['price']:,.0f} MAD (confidence: {result['confidence']:.1%})")
            
            # Feature importance
            importance = model.get_feature_importance()
            if importance:
                print("📊 Top 3 important features:")
                for i, (feature, score) in enumerate(list(importance.items())[:3], 1):
                    print(f"   {i}. {feature}: {score:.3f}")
        
    except Exception as e:
        print(f"❌ Model test error: {e}")

async def main():
    """Main test function"""
    print("🔧 Morocco Car Price Prediction - API Tests\n")
    
    # Test 1: Local model testing
    test_model_locally()
    print("\n" + "-"*50 + "\n")
    
    # Test 2: API testing (requires running server)
    print("🌐 Note: Make sure the FastAPI server is running on localhost:8000")
    print("   You can start it with: python main.py\n")
    
    try:
        await test_api()
    except aiohttp.ClientConnectionError:
        print("❌ Could not connect to API server.")
        print("   Please start the server first: python main.py")
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())