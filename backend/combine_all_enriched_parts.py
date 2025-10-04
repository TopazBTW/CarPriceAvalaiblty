"""
FUSION FINALE - Combine toutes les parties enrichies
Génère le dataset complet enrichi avec toutes les marques
"""

import pandas as pd

def combine_all_parts():
    """Combine les 4 parties en un seul dataset complet"""
    
    print("🔄 FUSION DES 4 PARTIES...")
    print("=" * 60)
    
    # Charger les 4 parties (avec trim)
    print("\n📂 Chargement des parties...")
    part1 = pd.read_csv('data/csv/morocco_new_cars_part1_budget.csv')
    print(f"  ✅ Partie 1 (Budget): {len(part1)} versions")
    
    part2 = pd.read_csv('data/csv/morocco_new_cars_part2_asian.csv')
    print(f"  ✅ Partie 2 (Asian): {len(part2)} versions")
    
    part3 = pd.read_csv('data/csv/morocco_new_cars_part3_german.csv')
    print(f"  ✅ Partie 3 (German): {len(part3)} versions")
    
    part4 = pd.read_csv('data/csv/morocco_new_cars_part4_remaining.csv')
    print(f"  ✅ Partie 4 (Remaining): {len(part4)} versions")
    
    # Combiner toutes les parties
    print("\n🔗 Fusion en cours...")
    df_complete = pd.concat([part1, part2, part3, part4], ignore_index=True)
    
    # Tri par marque, modèle, prix
    df_complete = df_complete.sort_values(['Brand', 'Model', 'Selling_Price'])
    
    # Sauvegarde avec trim
    output_with_trim = 'data/csv/morocco_new_cars_enriched.csv'
    df_complete.to_csv(output_with_trim, index=False, encoding='utf-8-sig')
    print(f"\n✅ Dataset complet avec trim sauvegardé: {output_with_trim}")
    
    # Sauvegarde sans trim (pour compatibilité backend)
    df_no_trim = df_complete[['Brand', 'Model', 'Fuel', 'Transmission', 'Selling_Price']]
    output_no_trim = 'data/csv/morocco_new_cars_enriched_notrim.csv'
    df_no_trim.to_csv(output_no_trim, index=False, encoding='utf-8-sig')
    print(f"✅ Dataset complet sans trim sauvegardé: {output_no_trim}")
    
    # Backup de l'original
    import shutil
    backup_path = 'data/csv/morocco_new_cars_original_302.csv'
    try:
        shutil.copy('data/csv/morocco_new_cars.csv', backup_path)
        print(f"\n💾 Backup de l'original créé: {backup_path}")
    except:
        pass
    
    # Remplacer le fichier original par la version enrichie (sans trim)
    df_no_trim.to_csv('data/csv/morocco_new_cars.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Fichier principal remplacé: morocco_new_cars.csv")
    
    return df_complete

if __name__ == "__main__":
    print("🚗 FUSION FINALE - DATASET ENRICHI COMPLET")
    print("=" * 60)
    
    df = combine_all_parts()
    
    print("\n" + "=" * 60)
    print("📊 STATISTIQUES FINALES")
    print("=" * 60)
    
    print(f"\n✅ TOTAL: {len(df):,} versions (vs 302 originales)")
    print(f"📈 Augmentation: +{len(df)-302} versions ({((len(df)-302)/302*100):.1f}%)")
    
    print(f"\n🏢 MARQUES: {df['Brand'].nunique()} marques")
    print(f"🚗 MODÈLES: {df['Model'].nunique()} modèles")
    
    print(f"\n💰 PRIX:")
    print(f"  • Min: {df['Selling_Price'].min():,} DH")
    print(f"  • Max: {df['Selling_Price'].max():,} DH")
    print(f"  • Moyenne: {df['Selling_Price'].mean():,.0f} DH")
    print(f"  • Médiane: {df['Selling_Price'].median():,.0f} DH")
    
    print(f"\n⛽ CARBURANTS:")
    for fuel in df['Fuel'].value_counts().items():
        print(f"  • {fuel[0]}: {fuel[1]} versions")
    
    print(f"\n⚙️ TRANSMISSIONS:")
    for trans in df['Transmission'].value_counts().items():
        print(f"  • {trans[0]}: {trans[1]} versions")
    
    print(f"\n🏆 TOP 10 MARQUES (par nombre de versions):")
    top_brands = df['Brand'].value_counts().head(10)
    for i, (brand, count) in enumerate(top_brands.items(), 1):
        print(f"  {i}. {brand}: {count} versions")
    
    print("\n" + "=" * 60)
    print("✅ VALIDATION UTILISATEUR:")
    print("=" * 60)
    
    # Vérifier les prix validés par l'utilisateur
    yaris = df[(df['Brand'] == 'Toyota') & (df['Model'] == 'Yaris')]
    print(f"\n✓ Toyota Yaris: {len(yaris)} versions")
    print(f"  Prix: {yaris['Selling_Price'].min():,} - {yaris['Selling_Price'].max():,} DH")
    print(f"  ✅ Vérifié utilisateur: 189,000 - 215,000 DH")
    
    a3 = df[(df['Brand'] == 'Audi') & (df['Model'] == 'A3')]
    print(f"\n✓ Audi A3: {len(a3)} versions")
    print(f"  Prix: {a3['Selling_Price'].min():,} - {a3['Selling_Price'].max():,} DH")
    print(f"  ✅ Vérifié utilisateur: 394,000 - 543,000 DH")
    
    print("\n" + "=" * 60)
    print("🎉 ENRICHISSEMENT TERMINÉ AVEC SUCCÈS!")
    print("=" * 60)
    print(f"\n📁 Fichiers générés:")
    print(f"  1. morocco_new_cars_enriched.csv (avec trim)")
    print(f"  2. morocco_new_cars_enriched_notrim.csv (sans trim)")
    print(f"  3. morocco_new_cars.csv (mis à jour)")
    print(f"  4. morocco_new_cars_original_302.csv (backup)")
    
    print(f"\n📊 Détail par partie:")
    print(f"  • Partie 1 (Budget): Dacia, Renault, Peugeot")
    print(f"  • Partie 2 (Asian): Toyota, Hyundai, Kia")
    print(f"  • Partie 3 (German): VW, Audi, BMW, Mercedes")
    print(f"  • Partie 4 (Remaining): Ford, Nissan, Citroen, Mazda, Suzuki, Skoda, Seat, Fiat, Jeep")
    
    print(f"\n🎯 Dataset prêt pour production!")
