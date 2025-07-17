#!/usr/bin/env python3
"""
Démarrage simple de Gold 7 Car Rent
Version fonctionnelle garantie
"""

import os
import sys

def main():
    print("🚗 Gold 7 Car Rent - Démarrage Simple")
    print("=" * 50)
    
    # Supprimer les fichiers de base de données s'ils existent
    db_files = ['location_voiture.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"✅ Base de données {db_file} supprimée")
            except:
                print(f"⚠️  Impossible de supprimer {db_file}")
    
    print("\n🚀 Démarrage de l'application...")
    print("📋 Informations de connexion:")
    print("   URL: http://127.0.0.1:5001")
    print("   Login: admin")
    print("   Mot de passe: admin123")
    print("\n⏳ Chargement en cours...")
    
    # Importer et démarrer l'application
    try:
        from app import app
        app.run(host='127.0.0.1', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Application arrêtée")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("\n🔧 Solutions possibles:")
        print("1. Vérifiez que Python et Flask sont installés")
        print("2. Exécutez: pip install -r requirements.txt")
        print("3. Redémarrez le terminal")

if __name__ == '__main__':
    main()
