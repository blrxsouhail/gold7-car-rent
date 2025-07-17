#!/bin/bash

echo "========================================"
echo "  Gold 7 Car Rent - Script de Déploiement"
echo "========================================"
echo

echo "Vérification des fichiers nécessaires..."
if [ ! -f "app.py" ]; then
    echo "ERREUR: app.py non trouvé!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "ERREUR: requirements.txt non trouvé!"
    exit 1
fi

echo "Tous les fichiers sont présents!"
echo

echo "Choisissez votre option de déploiement:"
echo
echo "1. Heroku (Recommandé)"
echo "2. Vercel (Simple)"
echo "3. Railway (Moderne)"
echo "4. Préparation GitHub seulement"
echo "5. Test local"
echo

read -p "Entrez votre choix (1-5): " choice

case $choice in
    1)
        echo
        echo "========================================"
        echo "  Déploiement Heroku"
        echo "========================================"
        echo
        echo "Assurez-vous d'avoir installé:"
        echo "- Git"
        echo "- Heroku CLI"
        echo
        echo "Commandes à exécuter:"
        echo
        echo "git init"
        echo "git add ."
        echo "git commit -m 'Initial commit - Gold 7 Car Rent'"
        echo "heroku login"
        echo "heroku create gold7-car-rent-[VOTRE-NOM]"
        echo "git push heroku main"
        echo "heroku open"
        echo
        ;;
    2)
        echo
        echo "========================================"
        echo "  Déploiement Vercel"
        echo "========================================"
        echo
        echo "Étapes:"
        echo "1. Créez un compte sur github.com"
        echo "2. Uploadez tous vos fichiers sur GitHub"
        echo "3. Créez un compte sur vercel.com"
        echo "4. Connectez votre repository GitHub"
        echo "5. Déployez automatiquement"
        echo
        ;;
    3)
        echo
        echo "========================================"
        echo "  Déploiement Railway"
        echo "========================================"
        echo
        echo "Étapes:"
        echo "1. Créez un compte sur railway.app"
        echo "2. Connectez votre GitHub"
        echo "3. Sélectionnez le repository"
        echo "4. Déployez en un clic"
        echo
        ;;
    4)
        echo
        echo "========================================"
        echo "  Préparation GitHub"
        echo "========================================"
        echo
        echo "Initialisation du repository Git..."
        git init
        git add .
        git commit -m "Initial commit - Gold 7 Car Rent"
        echo
        echo "Repository Git créé avec succès!"
        echo "Maintenant:"
        echo "1. Créez un repository sur github.com"
        echo "2. Suivez les instructions pour pusher votre code"
        echo
        ;;
    5)
        echo
        echo "========================================"
        echo "  Test Local"
        echo "========================================"
        echo
        echo "Lancement de l'application en local..."
        python run.py
        ;;
    *)
        echo
        echo "Choix invalide! Veuillez choisir entre 1 et 5."
        ;;
esac

echo
echo "========================================"
echo "  Déploiement terminé!"
echo "========================================"
echo
echo "Votre application Gold 7 Car Rent est prête!"
echo
echo "Identifiants de connexion:"
echo "Code d'accès: gold72025car"
echo "Mot de passe: gold72025car"
echo
