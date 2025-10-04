// Configuration for API integration
export const config = {
  // Backend API base URL
  apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  
  // API endpoints
  endpoints: {
    brands: '/brands',
    models: (brand: string) => `/brands/${encodeURIComponent(brand)}/models`,
    predict: '/predict',
    search: '/search',
    searchCars: '/search-cars',
    scrapingStatus: '/scraping-status',
    scrapedResults: '/scraped-results'
  },
  
  // Default configuration
  defaults: {
    searchLimit: 20,
    timeout: 30000, // 30 seconds
  }
}

// Helper function to build full API URLs
export const getApiUrl = (endpoint: string) => {
  return `${config.apiBaseUrl}${endpoint}`
}

// Helper function to make API calls with error handling
export const apiCall = async (endpoint: string, options?: RequestInit) => {
  const url = getApiUrl(endpoint)
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      },
      ...options
    })
    
    if (!response.ok) {
      throw new Error(`API call failed: ${response.status} ${response.statusText}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('API call error:', error)
    throw error
  }
}