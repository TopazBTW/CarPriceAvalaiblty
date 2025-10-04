"""
ANALYSE DES MARQUES/MODÈLES MANQUANTS - MARCHÉ MAROCAIN 2025
Identification des gaps dans le dataset actuel
"""

# MARQUES ACTUELLES (19):
# Dacia, Renault, Peugeot, Toyota, Hyundai, Kia, VW, Audi, BMW, Mercedes,
# Ford, Nissan, Citroen, Mazda, Suzuki, Skoda, Seat, Fiat, Jeep

# ===================================================================
# MARQUES MANQUANTES POPULAIRES AU MAROC
# ===================================================================

MARQUES_MANQUANTES = {
    # MARQUES CHINOISES (très populaires au Maroc)
    "Chery": ["Tiggo 4 Pro", "Tiggo 7 Pro", "Tiggo 8 Pro", "Arrizo 6"],
    "Haval": ["Jolion", "H6", "Dargo"],
    "MG": ["MG ZS", "MG 5", "MG HS"],
    "Geely": ["Coolray", "Emgrand X7"],
    "Omoda": ["Omoda 5", "Omoda C5"],
    "GAC": ["GS3", "GS8", "Emzoom"],
    "Dfsk": ["Glory 580", "Glory 500"],
    
    # MARQUES EUROPÉENNES
    "Alfa Romeo": ["Giulia", "Stelvio"],
    "Volvo": ["XC40", "XC60", "XC90", "S60", "S90"],
    "Mini": ["Cooper", "Countryman", "Clubman"],
    "Land Rover": ["Defender", "Discovery", "Range Rover Evoque", "Range Rover Sport", "Range Rover"],
    "Jaguar": ["E-Pace", "F-Pace", "XE", "XF"],
    "Porsche": ["Macan", "Cayenne", "Panamera"],
    
    # MARQUES AMÉRICAINES
    "Cadillac": ["XT4", "XT5", "XT6", "Escalade"],
    "Chevrolet": ["Captiva", "Trailblazer", "Silverado"],
    "GMC": ["Sierra", "Yukon"],
    
    # MARQUES ASIATIQUES
    "Mitsubishi": ["Mirage", "Attrage", "ASX", "Outlander", "L200"],
    "Subaru": ["XV", "Forester", "Outback"],
    "Lexus": ["UX", "NX", "RX", "ES", "LS", "LX"],
    "Infiniti": ["Q30", "QX50", "QX60", "QX80"],
    "Honda": ["City", "Civic", "Accord", "HR-V", "CR-V"],
    "Isuzu": ["D-Max", "MU-X"],
    "SsangYong": ["Tivoli", "Korando", "Rexton"],
}

# ===================================================================
# MODÈLES MANQUANTS POUR MARQUES EXISTANTES
# ===================================================================

MODELES_MANQUANTS_MARQUES_EXISTANTES = {
    "Toyota": ["Camry", "Prado", "Fortuner", "C-HR", "Proace"],
    "Nissan": ["Kicks", "Navara", "Sunny"],
    "Hyundai": ["Elantra", "Sonata", "Kona", "Palisade", "Creta"],
    "Kia": ["Seltos", "Carnival", "K5", "EV6"],
    "Volkswagen": ["T-Roc", "Arteon", "Caddy", "Transporter"],
    "Audi": ["A5", "A6", "A7", "A8", "Q7", "Q8", "e-tron"],
    "BMW": ["Série 5", "Série 6", "Série 7", "X4", "X5", "X6", "X7", "iX"],
    "Mercedes": ["CLA", "CLS", "Classe S", "GLE", "GLS", "G-Class", "EQC"],
    "Ford": "Explorer", "Bronco", "Edge", "Transit"],
    "Renault": ["Talisman", "Espace", "Trafic", "Arkana"],
    "Peugeot": ["Rifter", "Partner", "Boxer", "Traveller", "e-208", "e-2008"],
    "Citroen": ["SpaceTourer", "Jumpy", "Dispatch"],
    "Fiat": "Panda", "Doblo", "Ducato", "Fullback"],
    "Jeep": ["Wrangler", "Gladiator"],
    "Nissan": ["370Z", "GT-R"],
    "Mazda": ["MX-5", "Mazda6"],
    "Seat": ["Tarraco", "Alhambra"],
    "Skoda": ["Kamiq", "Enyaq", "Superb"],
}

print("📊 ANALYSE COMPLÈTE:")
print(f"Marques manquantes: {len(MARQUES_MANQUANTES)}")
print(f"Modèles additionnels pour marques existantes: {sum(len(v) for v in MODELES_MANQUANTS_MARQUES_EXISTANTES.values())}")
print(f"\nTOTAL ESTIMÉ À AJOUTER: ~1500-2000 versions supplémentaires")
