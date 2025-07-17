#!/usr/bin/env python3
"""
Script de réinitialisation de la base de données avec support employés
Gold 7 Car Rent v2.2.0
"""

import os
import sys
from app import app, db, Employe, CategorieDepense

def reset_database():
    """Réinitialise complètement la base de données avec la table employé"""
    
    print("🔄 Réinitialisation de la base de données avec support employés...")
    
    # Supprimer la base existante
    db_files = ['location_voiture.db', 'instance/location_voiture.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"✅ Base de données {db_file} supprimée")
            except Exception as e:
                print(f"⚠️  Erreur suppression {db_file}: {e}")
    
    # Supprimer le dossier instance
    if os.path.exists('instance'):
        try:
            import shutil
            shutil.rmtree('instance')
            print("✅ Dossier instance supprimé")
        except Exception as e:
            print(f"⚠️  Erreur suppression instance: {e}")
    
    print("\n🏗️  Création de la nouvelle base de données...")
    
    with app.app_context():
        try:
            # Créer toutes les tables
            db.create_all()
            print("✅ Tables créées avec succès")
            
            # Créer les dossiers nécessaires
            os.makedirs('static/uploads/clients', exist_ok=True)
            print("✅ Dossiers créés")
            
            # Créer les catégories de dépenses par défaut
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
            
            # Créer un employé par défaut
            if not Employe.query.filter_by(username='employe1').first():
                employe_defaut = Employe(
                    nom='Employé',
                    prenom='Test',
                    username='employe1',
                    password='employe123',
                    role='employe',
                    telephone='+212600000000',
                    email='employe@gold7carrent.com'
                )
                db.session.add(employe_defaut)
                print("✅ Employé par défaut créé")
            
            # Créer un admin employé
            if not Employe.query.filter_by(username='admin').first():
                admin_employe = Employe(
                    nom='Administrateur',
                    prenom='Système',
                    username='admin',
                    password='admin123',
                    role='admin',
                    telephone='+212600000001',
                    email='admin@gold7carrent.com'
                )
                db.session.add(admin_employe)
                print("✅ Admin employé créé")
            
            db.session.commit()
            
            print("\n🎉 Base de données initialisée avec succès!")
            print("\n📋 Comptes disponibles:")
            print("   👨‍💼 Admin système: gold72025car / gold72025car")
            print("   👨‍💼 Admin employé: admin / admin123")
            print("   👨‍💻 Employé: employe1 / employe123")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation: {e}")
            return False

if __name__ == '__main__':
    if reset_database():
        print("\n✅ Réinitialisation terminée avec succès!")
        print("🚀 Vous pouvez maintenant démarrer l'application avec: python start_simple.py")
    else:
        print("\n❌ Échec de la réinitialisation")
        sys.exit(1)
