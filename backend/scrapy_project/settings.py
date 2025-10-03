BOT_NAME = 'morocco_cars'

SPIDER_MODULES = ['scrapy_project.spiders']
NEWSPIDER_MODULE = 'scrapy_project.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure delays for requests
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# Configure pipelines
ITEM_PIPELINES = {
    'scrapy_project.pipelines.DataCleanupPipeline': 300,
    'scrapy_project.pipelines.CsvExportPipeline': 400,
}

# Configure user agent
USER_AGENT = 'morocco_cars (+http://www.yourdomain.com)'

# Enable autothrottling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Configure request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-MA,fr;q=0.9,en;q=0.8,ar;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Enable middleware
DOWNLOADER_MIDDLEWARES = {
    'scrapy_project.middlewares.RotateUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# Configure feeds (output formats)
FEEDS = {
    'used_cars_%(name)s_%(time)s.csv': {
        'format': 'csv',
        'encoding': 'utf8',
        'store_empty': False,
        'fields': ['brand', 'model', 'year', 'price', 'mileage', 'fuel_type', 'transmission', 'city', 'url', 'images', 'phone', 'description']
    }
}