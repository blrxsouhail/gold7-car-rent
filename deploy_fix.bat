@echo off
echo ========================================
echo   Gold 7 Car Rent - Correction Deploiement
echo ========================================
echo.

echo Le deploiement Vercel a echoue avec l'erreur DEPLOYMENT_NOT_FOUND
echo Voici les solutions alternatives plus fiables:
echo.

echo 1. Render.com (RECOMMANDE - Le plus fiable pour Flask)
echo 2. Heroku (Tres stable)
echo 3. Railway (Moderne)
echo 4. PythonAnywhere (Specialise Python)
echo 5. Corriger et reessayer Vercel
echo.

set /p choice="Choisissez votre solution (1-5): "

if "%choice%"=="1" goto render
if "%choice%"=="2" goto heroku
if "%choice%"=="3" goto railway
if "%choice%"=="4" goto pythonanywhere
if "%choice%"=="5" goto vercel_fix
goto invalid

:render
echo.
echo ========================================
echo   Solution Render.com (RECOMMANDEE)
echo ========================================
echo.
echo Render.com est optimise pour Flask et tres fiable.
echo.
echo Etapes:
echo 1. Allez sur github.com et creez un repository "gold7-car-rent"
echo 2. Uploadez tous vos fichiers sur GitHub
echo 3. Allez sur render.com et creez un compte gratuit
echo 4. Cliquez "New +" puis "Web Service"
echo 5. Connectez GitHub et selectionnez votre repository
echo 6. Configuration:
echo    - Name: gold7-car-rent
echo    - Environment: Python 3
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: python app.py
echo 7. Cliquez "Create Web Service"
echo.
echo URL finale: https://gold7-car-rent.onrender.com
echo.
pause
goto end

:heroku
echo.
echo ========================================
echo   Solution Heroku (TRES STABLE)
echo ========================================
echo.
echo Assurez-vous d'avoir installe Git et Heroku CLI
echo.
echo Commandes a executer:
echo.
echo git init
echo git add .
echo git commit -m "Gold 7 Car Rent - Deploiement"
echo heroku login
echo heroku create gold7-car-rent-unique-name
echo git push heroku main
echo heroku open
echo.
pause
goto end

:railway
echo.
echo ========================================
echo   Solution Railway (MODERNE)
echo ========================================
echo.
echo Etapes:
echo 1. Uploadez vos fichiers sur GitHub
echo 2. Allez sur railway.app
echo 3. Connectez GitHub
echo 4. Selectionnez votre repository
echo 5. Deployez automatiquement
echo.
pause
goto end

:pythonanywhere
echo.
echo ========================================
echo   Solution PythonAnywhere (SPECIALISE)
echo ========================================
echo.
echo Etapes:
echo 1. Creez un compte sur pythonanywhere.com
echo 2. Uploadez vos fichiers via l'interface web
echo 3. Configurez l'application Flask dans l'onglet "Web"
echo 4. Activez l'application
echo.
pause
goto end

:vercel_fix
echo.
echo ========================================
echo   Correction Vercel
echo ========================================
echo.
echo J'ai cree des fichiers corriges pour Vercel:
echo - api/index.py (nouveau point d'entree)
echo - vercel.json (configuration mise a jour)
echo.
echo Etapes pour reessayer:
echo 1. Uploadez TOUS les fichiers (y compris api/index.py) sur GitHub
echo 2. Allez sur vercel.com
echo 3. Cliquez "New Project"
echo 4. Selectionnez votre repository
echo 5. Configuration:
echo    - Framework Preset: Other
echo    - Build Command: pip install -r requirements.txt
echo    - Output Directory: (laisser vide)
echo 6. Deployez
echo.
echo ATTENTION: Vercel peut encore avoir des problemes avec Flask.
echo Render.com est plus fiable pour votre application.
echo.
pause
goto end

:invalid
echo.
echo Choix invalide! Veuillez choisir entre 1 et 5.
pause
goto end

:end
echo.
echo ========================================
echo   Informations Importantes
echo ========================================
echo.
echo Apres le deploiement, connectez-vous avec:
echo Code d'acces: gold72025car
echo Mot de passe: gold72025car
echo.
echo RECOMMANDATION: Utilisez Render.com pour un deploiement fiable!
echo.
pause
