from app import app, db, initialiser_donnees_base, corriger_transactions_manquantes

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialiser_donnees_base()
        corriger_transactions_manquantes()
        print("Base de données initialisée avec succès!")
    
    print("Démarrage de l'application Flask...")
    print("Accédez à l'application sur: http://127.0.0.1:5001")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5001, threaded=True)
    except OSError as e:
        print(f"Erreur de socket: {e}")
        print("Essai avec un autre port...")
        try:
            app.run(debug=True, host='127.0.0.1', port=5002, threaded=True)
        except OSError as e2:
            print(f"Erreur de socket sur le port 5002: {e2}")
            print("Essai avec localhost...")
            app.run(debug=True, host='localhost', port=5003, threaded=True)
