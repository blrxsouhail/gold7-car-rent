@echo off
echo ========================================
echo   Gold 7 Car Rent - Script de Deploiement
echo ========================================
echo.

echo Verification des fichiers necessaires...
if not exist "app.py" (
    echo ERREUR: app.py non trouve!
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERREUR: requirements.txt non trouve!
    pause
    exit /b 1
)

echo Tous les fichiers sont presents!
echo.

echo Choisissez votre option de deploiement:
echo.
echo 1. Heroku (Recommande)
echo 2. Vercel (Simple)
echo 3. Railway (Moderne)
echo 4. Preparation GitHub seulement
echo 5. Test local
echo.

set /p choice="Entrez votre choix (1-5): "

if "%choice%"=="1" goto heroku
if "%choice%"=="2" goto vercel
if "%choice%"=="3" goto railway
if "%choice%"=="4" goto github
if "%choice%"=="5" goto local
goto invalid

:heroku
echo.
echo ========================================
echo   Deploiement Heroku
echo ========================================
echo.
echo Assurez-vous d'avoir installe:
echo - Git
echo - Heroku CLI
echo.
echo Commandes a executer:
echo.
echo git init
echo git add .
echo git commit -m "Initial commit - Gold 7 Car Rent"
echo heroku login
echo heroku create gold7-car-rent-[VOTRE-NOM]
echo git push heroku main
echo heroku open
echo.
pause
goto end

:vercel
echo.
echo ========================================
echo   Deploiement Vercel
echo ========================================
echo.
echo Etapes:
echo 1. Creez un compte sur github.com
echo 2. Uploadez tous vos fichiers sur GitHub
echo 3. Creez un compte sur vercel.com
echo 4. Connectez votre repository GitHub
echo 5. Deployez automatiquement
echo.
pause
goto end

:railway
echo.
echo ========================================
echo   Deploiement Railway
echo ========================================
echo.
echo Etapes:
echo 1. Creez un compte sur railway.app
echo 2. Connectez votre GitHub
echo 3. Selectionnez le repository
echo 4. Deployez en un clic
echo.
pause
goto end

:github
echo.
echo ========================================
echo   Preparation GitHub
echo ========================================
echo.
echo Initialisation du repository Git...
git init
git add .
git commit -m "Initial commit - Gold 7 Car Rent"
echo.
echo Repository Git cree avec succes!
echo Maintenant:
echo 1. Creez un repository sur github.com
echo 2. Suivez les instructions pour pusher votre code
echo.
pause
goto end

:local
echo.
echo ========================================
echo   Test Local
echo ========================================
echo.
echo Lancement de l'application en local...
python run.py
goto end

:invalid
echo.
echo Choix invalide! Veuillez choisir entre 1 et 5.
pause
goto end

:end
echo.
echo ========================================
echo   Deploiement termine!
echo ========================================
echo.
echo Votre application Gold 7 Car Rent est prete!
echo.
echo Identifiants de connexion:
echo Code d'acces: gold72025car
echo Mot de passe: gold72025car
echo.
pause
