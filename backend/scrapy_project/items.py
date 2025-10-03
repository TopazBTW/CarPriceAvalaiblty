import scrapy
from scrapy import Item, Field

class UsedCarItem(scrapy.Item):
    # Car details
    brand = Field()
    model = Field()
    year = Field()
    price = Field()
    mileage = Field()
    fuel_type = Field()
    transmission = Field()
    
    # Location and contact
    city = Field()
    url = Field()
    images = Field()
    phone = Field()
    description = Field()
    
    # Metadata
    source = Field()
    scraped_at = Field()
    
    # Additional details
    body_type = Field()
    color = Field()
    engine_size = Field()
    condition = Field()