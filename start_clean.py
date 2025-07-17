#!/usr/bin/env python3
"""
Script de démarrage propre pour Gold 7 Car Rent
Résout les problèmes de base de données et démarre l'application
"""

import os
import sys
import shutil
from app import app, db

def clean_start():
    """Démarrage propre avec nettoyage complet"""
    
    print("🚗 Gold 7 Car Rent - Démarrage Propre")
    print("=" * 50)
    
    # Supprimer tous les fichiers de base de données
    files_to_remove = [
        'location_voiture.db',
        'instance/location_voiture.db'
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Supprimé: {file_path}")
            except Exception as e:
                print(f"⚠️  Erreur suppression {file_path}: {e}")
    
    # Supprimer le dossier instance
    if os.path.exists('instance'):
        try:
            shutil.rmtree('instance')
            print("✅ Dossier instance supprimé")
        except Exception as e:
            print(f"⚠️  Erreur suppression instance: {e}")
    
    # Supprimer les uploads existants
    if os.path.exists('static/uploads'):
        try:
            shutil.rmtree('static/uploads')
            print("✅ Dossier uploads supprimé")
        except Exception as e:
            print(f"⚠️  Erreur suppression uploads: {e}")
    
    print("\n🔄 Création de la nouvelle base de données...")
    
    with app.app_context():
        try:
            # Créer toutes les tables
            db.create_all()
            print("✅ Tables créées avec succès")
            
            # Créer les dossiers nécessaires
            os.makedirs('static/uploads/clients', exist_ok=True)
            print("✅ Dossiers créés")
            
            # Créer les catégories de dépenses par défaut
            from app import CategorieDepense
            categories_defaut = [
                'Carburant',
                'Maintenance',
                'Assurance',
                'Réparations',
                'Pièces détachées',
                'Nettoyage',
                'Frais administratifs',
                'Autres'
            ]
            
            for nom_categorie in categories_defaut:
                if not CategorieDepense.query.filter_by(nom=nom_categorie).first():
                    nouvelle_categorie = CategorieDepense(nom=nom_categorie)
                    db.session.add(nouvelle_categorie)
            
            db.session.commit()
            print("✅ Catégories de dépenses créées")
            
            print("\n🎉 Base de données initialisée avec succès!")
            print("\n📋 Informations de connexion:")
            print("   URL: http://127.0.0.1:5001")
            print("   Login: admin")
            print("   Mot de passe: admin123")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation: {e}")
            return False

def start_application():
    """Démarrer l'application Flask"""
    print("\n🚀 Démarrage de l'application...")
    try:
        app.run(host='127.0.0.1', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Application arrêtée par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")

if __name__ == '__main__':
    print("🔧 Nettoyage et initialisation...")
    
    if clean_start():
        print("\n✅ Système prêt!")
        
        # Demander si on veut démarrer immédiatement
        if len(sys.argv) > 1 and sys.argv[1] == '--start':
            start_application()
        else:
            response = input("\n🚀 Démarrer l'application maintenant? (y/N): ").lower().strip()
            if response in ['y', 'yes', 'oui']:
                start_application()
            else:
                print("\n📝 Pour démarrer plus tard, utilisez: python run.py")
                print("   ou: python start_clean.py --start")
    else:
        print("\n❌ Échec de l'initialisation")
        sys.exit(1)
