// Types pour la base de données des voitures
interface CarModelData {
  years: number[];
  fuels: string[];
  transmissions: string[];
  typical_km: number[];
  price_range: [number, number];
}

interface BrandData {
  [modelName: string]: CarModelData;
}

interface CarDatabase {
  [brandName: string]: BrandData;
}

// Base de données des voitures populaires au Maroc avec leurs spécifications
export const moroccanCarDatabase: CarDatabase = {
  'Toyota': {
    'Yaris': {
      years: [2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Hybrid'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [20000, 50000, 80000, 120000],
      price_range: [160000, 290000] // Prix réels neufs au Maroc: 160K-290K MAD
    },
    'Corolla': {
      years: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Hybrid'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [30000, 60000, 90000, 150000],
      price_range: [230000, 380000] // Prix réels neufs au Maroc: 230K-380K MAD
    },
    'Camry': {
      years: [2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Hybrid'],
      transmissions: ['Automatique'],
      typical_km: [25000, 55000, 85000, 130000],
      price_range: [420000, 650000] // Prix réels neufs au Maroc: 420K-650K MAD
    },
    'RAV4': {
      years: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Hybrid'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [35000, 70000, 110000, 160000],
      price_range: [380000, 580000] // Prix réels neufs au Maroc: 380K-580K MAD
    },
    'Land Cruiser': {
      years: [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
      fuels: ['Diesel', 'Essence'],
      transmissions: ['Automatique'],
      typical_km: [40000, 80000, 120000, 200000],
      price_range: [900000, 1500000] // Prix réels neufs au Maroc: 900K-1.5M MAD
    }
  },
  
  'Peugeot': {
    '208': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [25000, 55000, 85000, 130000],
      price_range: [190000, 280000] // Prix réels neufs au Maroc: 190K-280K MAD
    },
    '308': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [30000, 65000, 95000, 150000],
      price_range: [260000, 380000] // Prix réels neufs au Maroc: 260K-380K MAD
    },
    '2008': {
      years: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [28000, 60000, 90000, 140000],
      price_range: [280000, 420000] // Prix réels neufs au Maroc: 280K-420K MAD
    },
    '3008': {
      years: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel', 'Hybrid'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [32000, 68000, 100000, 160000],
      price_range: [380000, 550000] // Prix réels neufs au Maroc: 380K-550K MAD
    }
  },

  'Renault': {
    'Clio': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [25000, 55000, 85000, 130000],
      price_range: [65000, 130000]
    },
    'Megane': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [30000, 65000, 95000, 150000],
      price_range: [85000, 170000]
    },
    'Captur': {
      years: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [28000, 60000, 90000, 140000],
      price_range: [95000, 185000]
    },
    'Kadjar': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [35000, 70000, 105000, 160000],
      price_range: [120000, 220000]
    }
  },

  'Dacia': {
    'Sandero': {
      years: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [30000, 65000, 95000, 150000],
      price_range: [140000, 190000] // Prix réels neufs au Maroc: 140K-190K MAD
    },
    'Logan': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [35000, 70000, 105000, 160000],
      price_range: [150000, 200000] // Prix réels neufs au Maroc: 150K-200K MAD
    },
    'Duster': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [40000, 80000, 120000, 180000],
      price_range: [220000, 320000] // Prix réels neufs au Maroc: 220K-320K MAD
    }
  },

  'Hyundai': {
    'i10': {
      years: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [25000, 55000, 85000, 130000],
      price_range: [60000, 110000]
    },
    'i20': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [28000, 60000, 90000, 140000],
      price_range: [75000, 145000]
    },
    'Tucson': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel', 'Hybrid'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [35000, 70000, 105000, 160000],
      price_range: [140000, 280000]
    },
    'Elantra': {
      years: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [30000, 65000, 95000, 150000],
      price_range: [100000, 190000]
    }
  },

  'Kia': {
    'Picanto': {
      years: [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [25000, 55000, 85000, 130000],
      price_range: [55000, 105000]
    },
    'Rio': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [28000, 60000, 90000, 140000],
      price_range: [70000, 135000]
    },
    'Cerato': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [30000, 65000, 95000, 150000],
      price_range: [95000, 180000]
    },
    'Sportage': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel', 'Hybrid'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [35000, 70000, 105000, 160000],
      price_range: [135000, 270000]
    }
  },

  'Volkswagen': {
    'Polo': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [28000, 60000, 90000, 140000],
      price_range: [80000, 155000]
    },
    'Golf': {
      years: [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [32000, 68000, 100000, 160000],
      price_range: [110000, 210000]
    },
    'Tiguan': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [35000, 70000, 105000, 160000],
      price_range: [160000, 320000]
    }
  },

  'Ford': {
    'Fiesta': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [28000, 60000, 90000, 140000],
      price_range: [70000, 140000]
    },
    'Focus': {
      years: [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022],
      fuels: ['Essence', 'Diesel'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [32000, 68000, 100000, 160000],
      price_range: [90000, 175000]
    },
    'Kuga': {
      years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
      fuels: ['Essence', 'Diesel', 'Hybrid'],
      transmissions: ['Manuel', 'Automatique'],
      typical_km: [35000, 70000, 105000, 160000],
      price_range: [140000, 270000]
    }
  }
};

// Fonction pour obtenir les modèles disponibles pour une marque
export function getModelsForBrand(brand: string): string[] {
  const brandData = moroccanCarDatabase[brand];
  return brandData ? Object.keys(brandData) : [];
}

// Fonction pour obtenir les années disponibles pour un modèle
export function getYearsForModel(brand: string, model: string): number[] {
  const brandData = moroccanCarDatabase[brand];
  if (!brandData) return [];
  
  const modelData = brandData[model];
  return modelData ? modelData.years : [];
}

// Fonction pour obtenir les types de carburant disponibles
export function getFuelTypesForModel(brand: string, model: string): string[] {
  const brandData = moroccanCarDatabase[brand];
  if (!brandData) return [];
  
  const modelData = brandData[model];
  return modelData ? modelData.fuels : [];
}

// Fonction pour obtenir les transmissions disponibles
export function getTransmissionsForModel(brand: string, model: string): string[] {
  const brandData = moroccanCarDatabase[brand];
  if (!brandData) return [];
  
  const modelData = brandData[model];
  return modelData ? modelData.transmissions : [];
}

// Fonction pour obtenir les kilométrages typiques
export function getTypicalKilometersForModel(brand: string, model: string, year: number): number[] {
  const brandData = moroccanCarDatabase[brand];
  if (!brandData) return [50000, 100000, 150000];
  
  const modelData = brandData[model];
  if (!modelData) return [50000, 100000, 150000];
  
  // Ajuster selon l'âge de la voiture
  const currentYear = new Date().getFullYear();
  const carAge = currentYear - year;
  
  return modelData.typical_km.map((km: number) => Math.max(5000, km - (carAge * 10000)));
}

// Fonction pour obtenir la fourchette de prix estimée
export function getPriceRangeForModel(brand: string, model: string): [number, number] {
  const brandData = moroccanCarDatabase[brand];
  if (!brandData) return [50000, 200000];
  
  const modelData = brandData[model];
  return modelData ? modelData.price_range : [50000, 200000];
}

export function getAllBrands(): string[] {
  return Object.keys(moroccanCarDatabase);
}