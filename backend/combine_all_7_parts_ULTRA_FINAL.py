"""
FUSION ULTRA-FINALE: 7 PARTIES COMPLETES
1,113 versions avec 55 marques
"""

import pandas as pd
import os

def combine_all_7_parts_ULTRA_FINAL():
    """Fusionne les 7 parties pour un dataset complet de 55 marques"""
    
    print("=" * 70)
    print("FUSION ULTRA-FINALE - 7 PARTIES")
    print("=" * 70)
    
    # Charger les 7 parties
    print("\nChargement des 7 parties...")
    
    part1 = pd.read_csv('data/csv/morocco_new_cars_part1_budget.csv')
    print(f"  Partie 1 (Budget): {len(part1)} versions")
    
    part2 = pd.read_csv('data/csv/morocco_new_cars_part2_asian.csv')
    print(f"  Partie 2 (Asian): {len(part2)} versions")
    
    part3 = pd.read_csv('data/csv/morocco_new_cars_part3_german.csv')
    print(f"  Partie 3 (German): {len(part3)} versions")
    
    part4 = pd.read_csv('data/csv/morocco_new_cars_part4_remaining.csv')
    print(f"  Partie 4 (Remaining): {len(part4)} versions")
    
    part5 = pd.read_csv('data/csv/morocco_new_cars_part5_expansion.csv')
    print(f"  Partie 5 (Expansion): {len(part5)} versions")
    
    part6 = pd.read_csv('data/csv/morocco_new_cars_part6_final_brands.csv')
    print(f"  Partie 6 (Final Brands): {len(part6)} versions")
    
    part7 = pd.read_csv('data/csv/morocco_new_cars_part7_premium_luxe.csv')
    print(f"  Partie 7 (Premium/Luxe): {len(part7)} versions")
    
    # Fusionner
    print("\nFusion en cours...")
    df_complete = pd.concat([part1, part2, part3, part4, part5, part6, part7], ignore_index=True)
    df_complete = df_complete.sort_values(['Brand', 'Model', 'Selling_Price']).reset_index(drop=True)
    
    # Version sans trim
    df_notrim = df_complete.drop(columns=['Trim'])
    
    # Backup ancien fichier
    if os.path.exists('data/csv/morocco_new_cars.csv'):
        os.rename('data/csv/morocco_new_cars.csv', 'data/csv/morocco_new_cars_962versions_backup.csv')
        print("Backup cree: morocco_new_cars_962versions_backup.csv")
    
    # Sauvegarder
    df_complete.to_csv('data/csv/morocco_new_cars_ULTRA_FINAL.csv', index=False)
    df_notrim.to_csv('data/csv/morocco_new_cars_ULTRA_FINAL_notrim.csv', index=False)
    df_complete.to_csv('data/csv/morocco_new_cars.csv', index=False)
    
    print(f"\nDataset ultra-final: {len(df_complete)} versions")
    
    # Statistiques
    print("\n" + "=" * 70)
    print("STATISTIQUES ULTRA-FINALES")
    print("=" * 70)
    
    print(f"\nTOTAL: {len(df_complete)} versions")
    print(f"Evolution: 302 -> 726 -> 878 -> 962 -> {len(df_complete)} versions")
    print(f"Augmentation totale: +{len(df_complete) - 302} versions ({((len(df_complete) - 302) / 302 * 100):.1f}%)")
    
    print(f"\nMARQUES: {df_complete['Brand'].nunique()} marques")
    brands = sorted(df_complete['Brand'].unique())
    for i in range(0, len(brands), 10):
        print(f"  {', '.join(brands[i:i+10])}")
    
    print(f"\nMODELES: {df_complete['Model'].nunique()} modeles differents")
    
    print(f"\nPRIX:")
    print(f"  Min: {df_complete['Selling_Price'].min():,} DH (Chevrolet Spark)")
    print(f"  Max: {df_complete['Selling_Price'].max():,} DH (Ferrari SF90)")
    print(f"  Moyenne: {df_complete['Selling_Price'].mean():,.0f} DH")
    print(f"  Mediane: {df_complete['Selling_Price'].median():,.0f} DH")
    
    print(f"\nCARBURANTS:")
    for fuel, count in df_complete['Fuel'].value_counts().items():
        pct = (count / len(df_complete)) * 100
        print(f"  {fuel}: {count} versions ({pct:.1f}%)")
    
    print(f"\nTRANSMISSIONS:")
    for trans, count in df_complete['Transmission'].value_counts().items():
        pct = (count / len(df_complete)) * 100
        print(f"  {trans}: {count} versions ({pct:.1f}%)")
    
    print(f"\n20 NOUVELLES MARQUES (Partie 7):")
    part7_brands = sorted(part7['Brand'].unique())
    for brand in part7_brands:
        brand_data = df_complete[df_complete['Brand'] == brand]
        models = brand_data['Model'].nunique()
        versions = len(brand_data)
        print(f"  {brand:15} - {versions:3} versions ({models} modeles)")
    
    print(f"\nTOP 20 MARQUES (par nombre de versions):")
    top_brands = df_complete['Brand'].value_counts().head(20)
    for i, (brand, count) in enumerate(top_brands.items(), 1):
        print(f"  {i:2}. {brand:20}: {count:3} versions")
    
    # Nettoyage optionnel
    print("\n" + "=" * 70)
    print("NETTOYAGE (optionnel)")
    print("=" * 70)
    
    old_files = [
        'data/csv/morocco_new_cars_FINAL.csv',
        'data/csv/morocco_new_cars_FINAL_notrim.csv',
        'data/csv/morocco_new_cars_part7_premium_luxe_notrim.csv',
    ]
    
    deleted = 0
    for file in old_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Supprime: {os.path.basename(file)}")
            deleted += 1
    
    if deleted > 0:
        print(f"\n{deleted} fichiers nettoyes")
    
    print("\n" + "=" * 70)
    print("DATASET ULTRA-FINAL COMPLETE!")
    print("=" * 70)
    print(f"\n{len(df_complete)} versions couvrant {df_complete['Brand'].nunique()} marques")
    print(f"De {df_complete['Selling_Price'].min():,} DH a {df_complete['Selling_Price'].max():,} DH")
    print(f"\nFichiers crees:")
    print(f"  - morocco_new_cars.csv ({len(df_complete)} versions)")
    print(f"  - morocco_new_cars_ULTRA_FINAL.csv")
    print(f"  - morocco_new_cars_ULTRA_FINAL_notrim.csv")
    print("=" * 70)


if __name__ == "__main__":
    combine_all_7_parts_ULTRA_FINAL()
