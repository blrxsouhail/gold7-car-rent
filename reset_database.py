#!/usr/bin/env python3
"""
Script pour réinitialiser complètement la base de données
avec la nouvelle structure incluant le système de clients
"""

import os
import sys
from app import app, db

def reset_database():
    """Supprime et recrée la base de données avec la nouvelle structure"""
    
    with app.app_context():
        # Supprimer le fichier de base de données s'il existe
        db_path = 'location_voiture.db'
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"✅ Base de données {db_path} supprimée")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {db_path}: {e}")
                return False
        
        # Supprimer le dossier d'uploads s'il existe
        uploads_path = 'static/uploads'
        if os.path.exists(uploads_path):
            import shutil
            try:
                shutil.rmtree(uploads_path)
                print(f"✅ Dossier {uploads_path} supprimé")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {uploads_path}: {e}")
        
        try:
            # Recréer toutes les tables avec la nouvelle structure
            db.create_all()
            print("✅ Nouvelles tables créées avec succès")
            
            # Créer le dossier d'uploads
            os.makedirs('static/uploads/clients', exist_ok=True)
            print("✅ Dossier d'uploads créé")
            
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
            print("✅ Catégories de dépenses par défaut créées")
            
            print("\n🎉 Base de données réinitialisée avec succès!")
            print("📋 Nouvelle structure inclut:")
            print("   - Système de gestion des clients complet")
            print("   - Upload de photos (passeport et permis)")
            print("   - Liaison clients-réservations")
            print("   - Dashboard moderne")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables: {e}")
            return False

if __name__ == '__main__':
    print("🔄 Réinitialisation de la base de données...")
    print("⚠️  ATTENTION: Toutes les données existantes seront perdues!")
    
    # Demander confirmation en mode interactif
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        confirm = 'y'
    else:
        confirm = input("Continuer? (y/N): ").lower().strip()
    
    if confirm in ['y', 'yes', 'oui']:
        if reset_database():
            print("\n✅ Réinitialisation terminée avec succès!")
            print("🚀 Vous pouvez maintenant démarrer l'application avec: python run.py")
        else:
            print("\n❌ Échec de la réinitialisation")
            sys.exit(1)
    else:
        print("❌ Réinitialisation annulée")
        sys.exit(0)
