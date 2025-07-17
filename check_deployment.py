#!/usr/bin/env python3
"""
Script de vérification pour le déploiement de Gold 7 Car Rent
"""

import os
import sys

def check_file(filename, description):
    """Vérifie si un fichier existe"""
    if os.path.exists(filename):
        print(f"✅ {filename} - {description}")
        return True
    else:
        print(f"❌ {filename} - {description} (MANQUANT)")
        return False

def check_content(filename, required_content, description):
    """Vérifie si un fichier contient le contenu requis"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            if required_content in content:
                print(f"✅ {filename} contient {description}")
                return True
            else:
                print(f"⚠️  {filename} ne contient pas {description}")
                return False
    except FileNotFoundError:
        print(f"❌ {filename} non trouvé")
        return False

def main():
    print("🔍 Vérification des fichiers pour le déploiement")
    print("=" * 50)
    
    all_good = True
    
    # Fichiers essentiels
    essential_files = [
        ("app.py", "Application Flask principale"),
        ("requirements.txt", "Dépendances Python"),
        ("templates/base.html", "Template de base"),
        ("templates/login.html", "Page de connexion"),
        ("static/style.css", "Styles CSS"),
        ("static/images/logo.svg", "Logo de l'application")
    ]
    
    print("\n📁 Fichiers essentiels:")
    for filename, description in essential_files:
        if not check_file(filename, description):
            all_good = False
    
    # Fichiers de déploiement
    deployment_files = [
        ("Procfile", "Configuration Heroku"),
        ("runtime.txt", "Version Python"),
        ("vercel.json", "Configuration Vercel"),
        ("app.yaml", "Configuration Google App Engine"),
        (".gitignore", "Fichiers à ignorer"),
        ("README.md", "Documentation")
    ]
    
    print("\n🚀 Fichiers de déploiement:")
    for filename, description in deployment_files:
        if not check_file(filename, description):
            all_good = False
    
    # Vérifications de contenu
    print("\n🔍 Vérifications de contenu:")
    
    # Vérifier requirements.txt
    check_content("requirements.txt", "gunicorn", "gunicorn pour le déploiement")
    
    # Vérifier app.py
    check_content("app.py", "PORT", "configuration du port pour l'hébergement")
    check_content("app.py", "gold72025car", "identifiants de connexion")
    
    # Vérifier Procfile
    check_content("Procfile", "web: python app.py", "commande de démarrage")
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 TOUT EST PRÊT POUR LE DÉPLOIEMENT !")
        print("\nOptions de déploiement recommandées:")
        print("1. Vercel (le plus simple)")
        print("2. Heroku (le plus complet)")
        print("3. Railway (moderne)")
        print("\nConsultez DEPLOIEMENT_RAPIDE.md pour les instructions détaillées.")
    else:
        print("⚠️  CERTAINS FICHIERS SONT MANQUANTS")
        print("Assurez-vous que tous les fichiers sont présents avant le déploiement.")
    
    print("\n🔑 Identifiants de connexion:")
    print("Code d'accès: gold72025car")
    print("Mot de passe: gold72025car")

if __name__ == "__main__":
    main()
