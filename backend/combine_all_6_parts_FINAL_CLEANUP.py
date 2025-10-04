"""
FUSION FINALE + NETTOYAGE
Fusionne toutes les 6 parties et nettoie les anciens fichiers
"""

import pandas as pd
import os

def combine_all_6_parts():
    """Fusionne les 6 parties"""
    
    print("=" * 70)
    print("🚗 FUSION FINALE + NETTOYAGE")
    print("=" * 70)
    
    # Charger les 6 parties
    print("\n📂 Chargement des 6 parties...")
    
    part1 = pd.read_csv('data/csv/morocco_new_cars_part1_budget.csv')
    print(f"  ✅ Partie 1 (Budget): {len(part1)} versions")
    
    part2 = pd.read_csv('data/csv/morocco_new_cars_part2_asian.csv')
    print(f"  ✅ Partie 2 (Asian): {len(part2)} versions")
    
    part3 = pd.read_csv('data/csv/morocco_new_cars_part3_german.csv')
    print(f"  ✅ Partie 3 (German): {len(part3)} versions")
    
    part4 = pd.read_csv('data/csv/morocco_new_cars_part4_remaining.csv')
    print(f"  ✅ Partie 4 (Remaining): {len(part4)} versions")
    
    part5 = pd.read_csv('data/csv/morocco_new_cars_part5_expansion.csv')
    print(f"  ✅ Partie 5 (Expansion): {len(part5)} versions")
    
    part6 = pd.read_csv('data/csv/morocco_new_cars_part6_final_brands.csv')
    print(f"  ✅ Partie 6 (Final Brands): {len(part6)} versions")
    
    # Fusionner
    print("\n🔗 Fusion en cours...")
    df_complete = pd.concat([part1, part2, part3, part4, part5, part6], ignore_index=True)
    df_complete = df_complete.sort_values(['Brand', 'Model', 'Selling_Price']).reset_index(drop=True)
    
    # Version sans trim
    df_notrim = df_complete.drop(columns=['Trim'])
    
    # Sauvegarder
    df_complete.to_csv('data/csv/morocco_new_cars_FINAL.csv', index=False)
    df_notrim.to_csv('data/csv/morocco_new_cars_FINAL_notrim.csv', index=False)
    
    # Mettre à jour le fichier principal
    df_complete.to_csv('data/csv/morocco_new_cars.csv', index=False)
    
    print(f"✅ Dataset final: {len(df_complete)} versions")
    
    # Statistiques
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES FINALES")
    print("=" * 70)
    
    print(f"\n✅ TOTAL: {len(df_complete)} versions")
    print(f"📈 Evolution: 302 → 726 → 878 → {len(df_complete)} versions")
    print(f"📈 Augmentation totale: +{len(df_complete) - 302} versions ({((len(df_complete) - 302) / 302 * 100):.1f}%)")
    
    print(f"\n🏢 MARQUES: {df_complete['Brand'].nunique()} marques")
    brands = sorted(df_complete['Brand'].unique())
    print(f"  {', '.join(brands[:18])},")
    print(f"  {', '.join(brands[18:])}")
    
    print(f"\n🚗 MODÈLES: {df_complete['Model'].nunique()} modèles différents")
    
    print(f"\n💰 PRIX:")
    print(f"  • Min: {df_complete['Selling_Price'].min():,} DH")
    print(f"  • Max: {df_complete['Selling_Price'].max():,} DH")
    print(f"  • Moyenne: {df_complete['Selling_Price'].mean():,.0f} DH")
    print(f"  • Médiane: {df_complete['Selling_Price'].median():,.0f} DH")
    
    print(f"\n⛽ CARBURANTS:")
    for fuel, count in df_complete['Fuel'].value_counts().items():
        pct = (count / len(df_complete)) * 100
        print(f"  • {fuel}: {count} versions ({pct:.1f}%)")
    
    print(f"\n⚙️ TRANSMISSIONS:")
    for trans, count in df_complete['Transmission'].value_counts().items():
        pct = (count / len(df_complete)) * 100
        print(f"  • {trans}: {count} versions ({pct:.1f}%)")
    
    print(f"\n🌟 NOUVELLES MARQUES (Partie 6):")
    part6_brands = sorted(part6['Brand'].unique())
    for brand in part6_brands:
        brand_data = df_complete[df_complete['Brand'] == brand]
        models = brand_data['Model'].nunique()
        versions = len(brand_data)
        print(f"  • {brand}: {versions} versions ({models} modèles)")
    
    print(f"\n🏆 TOP 15 MARQUES (par nombre de versions):")
    top_brands = df_complete['Brand'].value_counts().head(15)
    for i, (brand, count) in enumerate(top_brands.items(), 1):
        print(f"  {i:2}. {brand:20}: {count:3} versions")
    
    # Nettoyage des anciens fichiers
    print("\n" + "=" * 70)
    print("🧹 NETTOYAGE DES ANCIENS FICHIERS")
    print("=" * 70)
    
    files_to_delete = [
        'data/csv/morocco_new_cars_726versions_backup.csv',
        'data/csv/morocco_new_cars_COMPLETE_enriched.csv',
        'data/csv/morocco_new_cars_COMPLETE_notrim.csv',
        'data/csv/morocco_new_cars_enriched.csv',
        'data/csv/morocco_new_cars_enriched_notrim.csv',
        'data/csv/morocco_new_cars_OLD_BACKUP.csv',
        'data/csv/morocco_new_cars_original_302.csv',
        'data/csv/morocco_new_cars_part1_budget_notrim.csv',
        'data/csv/morocco_new_cars_part2_asian_notrim.csv',
        'data/csv/morocco_new_cars_part3_german_notrim.csv',
        'data/csv/morocco_new_cars_part4_remaining_notrim.csv',
        'data/csv/morocco_new_cars_part5_expansion_notrim.csv',
        'data/csv/morocco_new_cars_part6_final_brands_notrim.csv',
    ]
    
    deleted_count = 0
    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)
            print(f"  ❌ Supprimé: {os.path.basename(file)}")
            deleted_count += 1
    
    print(f"\n✅ {deleted_count} fichiers supprimés")
    
    # Fichiers conservés
    print("\n📁 FICHIERS FINAUX CONSERVÉS:")
    kept_files = [
        'morocco_new_cars.csv',
        'morocco_new_cars_FINAL.csv',
        'morocco_new_cars_FINAL_notrim.csv',
        'morocco_new_cars_part1_budget.csv',
        'morocco_new_cars_part2_asian.csv',
        'morocco_new_cars_part3_german.csv',
        'morocco_new_cars_part4_remaining.csv',
        'morocco_new_cars_part5_expansion.csv',
        'morocco_new_cars_part6_final_brands.csv',
    ]
    
    for file in kept_files:
        filepath = f'data/csv/{file}'
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / 1024
            print(f"  ✅ {file:50} ({size:.1f} KB)")
    
    print("\n" + "=" * 70)
    print("🎉 DATASET COMPLET TERMINÉ!")
    print("=" * 70)
    print(f"\n🚀 {len(df_complete)} versions couvrant {df_complete['Brand'].nunique()} marques")
    print(f"📊 Prix: {df_complete['Selling_Price'].min():,} - {df_complete['Selling_Price'].max():,} DH")
    print(f"✅ Dataset prêt pour production ML!")
    print("=" * 70)


if __name__ == "__main__":
    combine_all_6_parts()
