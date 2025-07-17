from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from werkzeug.utils import secure_filename
import io
import os
import uuid
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gold7-car-rent-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///location_voiture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration pour l'upload de fichiers
app.config['UPLOAD_FOLDER'] = 'static/uploads/clients'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

db = SQLAlchemy(app)

# Créer le dossier d'upload s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialiser la base de données au premier démarrage
def init_database():
    """Initialise la base de données si elle n'existe pas"""
    try:
        # Tester si les tables existent
        Voiture.query.first()
    except:
        # Les tables n'existent pas, les créer
        print("🔄 Initialisation de la base de données...")
        db.create_all()

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

        db.session.commit()
        print("✅ Base de données initialisée avec succès!")
        print("✅ Employé par défaut créé : employe1 / employe123")

# L'initialisation sera faite après la définition de tous les modèles

# Fonctions utilitaires pour l'upload de fichiers
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, prefix=''):
    """Sauvegarde un fichier uploadé et retourne le nom du fichier"""
    if file and allowed_file(file.filename):
        # Générer un nom unique pour le fichier
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{prefix}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None

def delete_file(filename):
    """Supprime un fichier du dossier d'upload"""
    if filename:
        try:
            # Vérifier si UPLOAD_FOLDER est configuré
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
            file_path = os.path.join(upload_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Fichier supprimé: {file_path}")
            else:
                print(f"Fichier non trouvé: {file_path}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier {filename}: {e}")

# Informations de connexion
LOGIN_USERNAME = 'gold72025car'
LOGIN_PASSWORD = 'gold72025car'

# Décorateur pour protéger les routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            flash('Accès refusé. Droits administrateur requis.', 'error')
            return redirect(url_for('dashboard_employe'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_role():
    return session.get('user_role', 'employe')

# Modèles de données
class Employe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='employe')  # 'admin' ou 'employe'
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def __repr__(self):
        return f'<Employe {self.username}>'

class Voiture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    immatriculation = db.Column(db.String(20), unique=True, nullable=False)
    couleur = db.Column(db.String(50), nullable=False)
    km = db.Column(db.Integer, nullable=False)
    carburant = db.Column(db.String(20), nullable=False)  # diesel/essence
    disponible = db.Column(db.Boolean, default=True)
    
    reservations = db.relationship('Reservation', backref='voiture', lazy=True)
    vidanges = db.relationship('Vidange', backref='voiture', lazy=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_client = db.Column(db.String(100), nullable=False)
    date_depart = db.Column(db.Date, nullable=False)
    date_retour = db.Column(db.Date, nullable=False)
    jours = db.Column(db.Integer, nullable=False)
    prix_par_jour = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    voiture_id = db.Column(db.Integer, db.ForeignKey('voiture.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

class Vidange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    immatriculation = db.Column(db.String(20), nullable=False)
    derniere_vidange = db.Column(db.Integer, nullable=False)  # km
    prochaine_vidange = db.Column(db.Integer, nullable=False)  # km
    voiture_id = db.Column(db.Integer, db.ForeignKey('voiture.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

class Retour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_retour = db.Column(db.Date, nullable=False)
    heure_retour = db.Column(db.Time, nullable=False)
    nom_client = db.Column(db.String(100), nullable=False)
    voiture_id = db.Column(db.Integer, db.ForeignKey('voiture.id'), nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=True)
    km_retour = db.Column(db.Integer, nullable=True)  # Kilométrage au retour
    etat_vehicule = db.Column(db.String(200), nullable=True)  # État du véhicule
    commentaires = db.Column(db.Text, nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    voiture = db.relationship('Voiture', backref='retours')
    reservation = db.relationship('Reservation', backref='retour', uselist=False)

# Modèle Client
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Informations personnelles
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    lieu_naissance = db.Column(db.String(100), nullable=True)
    nationalite = db.Column(db.String(50), nullable=True)
    sexe = db.Column(db.String(10), nullable=True)  # M/F

    # Coordonnées
    telephone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    adresse = db.Column(db.Text, nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    code_postal = db.Column(db.String(10), nullable=True)
    pays = db.Column(db.String(50), default='Maroc')

    # Documents d'identité
    type_piece_identite = db.Column(db.String(50), nullable=False)  # Passeport, CIN, etc.
    numero_piece_identite = db.Column(db.String(50), nullable=False, unique=True)
    date_expiration_piece = db.Column(db.Date, nullable=True)
    photo_piece_identite = db.Column(db.String(200), nullable=True)  # Chemin vers la photo

    # Permis de conduire
    numero_permis = db.Column(db.String(50), nullable=False, unique=True)
    date_obtention_permis = db.Column(db.Date, nullable=False)
    date_expiration_permis = db.Column(db.Date, nullable=False)
    categorie_permis = db.Column(db.String(10), default='B')  # A, B, C, D, etc.
    pays_delivrance_permis = db.Column(db.String(50), default='Maroc')
    photo_permis = db.Column(db.String(200), nullable=True)  # Chemin vers la photo

    # Informations complémentaires
    profession = db.Column(db.String(100), nullable=True)
    entreprise = db.Column(db.String(100), nullable=True)
    personne_contact_urgence = db.Column(db.String(100), nullable=True)
    telephone_urgence = db.Column(db.String(20), nullable=True)

    # Statut et notes
    statut = db.Column(db.String(20), default='actif')  # actif, suspendu, blacklist
    notes = db.Column(db.Text, nullable=True)

    # Métadonnées
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations (pas de relation directe car pas de clé étrangère dans Reservation)

    def __repr__(self):
        return f'<Client {self.prenom} {self.nom}>'

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def age(self):
        if self.date_naissance:
            today = date.today()
            return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
        return None

    @property
    def permis_valide(self):
        if self.date_expiration_permis:
            return self.date_expiration_permis > date.today()
        return False

    @property
    def piece_identite_valide(self):
        if self.date_expiration_piece:
            return self.date_expiration_piece > date.today()
        return True  # Certaines pièces n'expirent pas

# Modèles comptables
class CategorieDepense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    couleur = db.Column(db.String(7), default='#6c757d')  # Code couleur hex
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    depenses = db.relationship('Depense', backref='categorie', lazy=True)

class Depense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    date_depense = db.Column(db.Date, nullable=False)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie_depense.id'), nullable=False)
    voiture_id = db.Column(db.Integer, db.ForeignKey('voiture.id'), nullable=True)  # Optionnel si lié à une voiture
    facture_numero = db.Column(db.String(50), nullable=True)
    fournisseur = db.Column(db.String(100), nullable=True)
    commentaires = db.Column(db.Text, nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    voiture = db.relationship('Voiture', backref='depenses')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_transaction = db.Column(db.String(20), nullable=False)  # 'recette' ou 'depense'
    description = db.Column(db.String(200), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    date_transaction = db.Column(db.Date, nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=True)
    depense_id = db.Column(db.Integer, db.ForeignKey('depense.id'), nullable=True)
    mode_paiement = db.Column(db.String(50), nullable=True)  # espèces, chèque, virement, etc.
    reference = db.Column(db.String(100), nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    reservation = db.relationship('Reservation', backref='transactions')
    depense = db.relationship('Depense', backref='transaction', uselist=False)

# Routes de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Vérifier d'abord l'admin par défaut
        if username == LOGIN_USERNAME and password == LOGIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            session['user_role'] = 'admin'
            session['user_id'] = 0  # ID spécial pour admin
            flash('Connexion administrateur réussie ! Bienvenue dans Gold 7 Car Rent.', 'success')
            return redirect(url_for('index'))

        # Vérifier les employés dans la base de données
        employe = Employe.query.filter_by(username=username, actif=True).first()
        if employe and employe.password == password:  # En production, utiliser un hash
            session['logged_in'] = True
            session['username'] = username
            session['user_role'] = employe.role
            session['user_id'] = employe.id
            session['user_nom'] = employe.nom_complet
            flash(f'Connexion réussie! Bienvenue {employe.nom_complet}', 'success')

            # Rediriger selon le rôle
            if employe.role == 'admin':
                return redirect(url_for('index'))
            else:
                return redirect(url_for('dashboard_employe'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('login'))

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

# Dashboard employé
@app.route('/employe')
@login_required
def dashboard_employe():
    # Vérifier que c'est bien un employé
    if session.get('user_role') == 'admin':
        return redirect(url_for('index'))

    # Statistiques limitées pour employés
    voitures_disponibles = Voiture.query.filter_by(disponible=True).count()
    voitures_louees = Voiture.query.filter_by(disponible=False).count()
    reservations_actives = Reservation.query.join(Voiture).filter(Voiture.disponible == False).count()

    # Réservations récentes (5 dernières)
    reservations_recentes = Reservation.query.order_by(Reservation.date_creation.desc()).limit(5).all()

    return render_template('dashboard_employe.html',
                         voitures_disponibles=voitures_disponibles,
                         voitures_louees=voitures_louees,
                         reservations_actives=reservations_actives,
                         reservations_recentes=reservations_recentes)

# Routes employés - Toutes les voitures avec statut et vidanges (LECTURE SEULE)
@app.route('/employe/voitures')
@login_required
def voitures_employe():
    if session.get('user_role') == 'admin':
        return redirect(url_for('voitures'))

    # Afficher toutes les voitures avec leur statut et informations de vidange
    voitures = Voiture.query.all()

    # Récupérer les informations de vidange pour chaque voiture
    voitures_avec_vidange = []
    for voiture in voitures:
        vidange = Vidange.query.filter_by(voiture_id=voiture.id).first()
        voitures_avec_vidange.append({
            'voiture': voiture,
            'vidange': vidange
        })

    return render_template('voitures_employe.html', voitures_avec_vidange=voitures_avec_vidange)

# Routes employés - Réservations (LECTURE SEULE)
@app.route('/employe/reservations')
@login_required
def reservations_employe():
    if session.get('user_role') == 'admin':
        return redirect(url_for('reservations'))

    # Affichage lecture seule des réservations
    reservations = Reservation.query.order_by(Reservation.date_creation.desc()).all()
    return render_template('reservations_employe.html', reservations=reservations)

# Routes employés - Retours (LECTURE SEULE)
@app.route('/employe/retours')
@login_required
def retours_employe():
    if session.get('user_role') == 'admin':
        return redirect(url_for('retours'))

    # Affichage lecture seule des retours
    retours = Retour.query.order_by(Retour.date_creation.desc()).all()
    return render_template('retours_employe.html', retours=retours)

# Routes employés - Vidanges (LECTURE SEULE)
@app.route('/employe/vidanges')
@login_required
def vidanges_employe():
    if session.get('user_role') == 'admin':
        return redirect(url_for('vidanges'))

    # Affichage lecture seule des vidanges
    vidanges = Vidange.query.order_by(Vidange.date_creation.desc()).all()
    return render_template('vidanges_employe.html', vidanges=vidanges)

# Routes principales
@app.route('/')
@login_required
def index():
    # Statistiques pour le dashboard
    voitures_count = Voiture.query.count()
    voitures_disponibles = Voiture.query.filter_by(disponible=True).count()
    voitures_louees = Voiture.query.filter_by(disponible=False).count()

    reservations_count = Reservation.query.count()
    reservations_actives = Reservation.query.join(Voiture).filter(Voiture.disponible == False).count()

    # Revenus du mois actuel
    today = date.today()
    debut_mois = today.replace(day=1)
    reservations_mois = Reservation.query.filter(Reservation.date_creation >= debut_mois).all()
    revenus_mois = sum(r.total for r in reservations_mois)

    # Maintenance due (voitures avec kilométrage élevé)
    maintenance_due = 0
    for voiture in Voiture.query.all():
        vidange = Vidange.query.filter_by(voiture_id=voiture.id).first()
        if vidange and voiture.km >= vidange.prochaine_vidange:
            maintenance_due += 1

    voitures_maintenance = maintenance_due

    return render_template('index_dashboard.html',
                         voitures_count=voitures_count,
                         voitures_disponibles=voitures_disponibles,
                         voitures_louees=voitures_louees,
                         voitures_maintenance=voitures_maintenance,
                         reservations_count=reservations_count,
                         reservations_actives=reservations_actives,
                         revenus_mois=revenus_mois,
                         maintenance_due=maintenance_due,
                         date=date)

# Routes pour les voitures
@app.route('/voitures')
@admin_required  # Seuls les admins peuvent gérer les voitures
def voitures():
    voitures = Voiture.query.all()
    return render_template('voitures.html', voitures=voitures)

@app.route('/voiture/ajouter', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent ajouter des voitures
def ajouter_voiture():
    if request.method == 'POST':
        nom = request.form['nom']
        immatriculation = request.form['immatriculation']
        couleur = request.form['couleur']
        km = int(request.form['km'])
        carburant = request.form['carburant']

        nouvelle_voiture = Voiture(
            nom=nom,
            immatriculation=immatriculation,
            couleur=couleur,
            km=km,
            carburant=carburant
        )

        try:
            db.session.add(nouvelle_voiture)
            db.session.commit()
            flash('Voiture ajoutée avec succès!', 'success')
            return redirect(url_for('voitures'))
        except:
            flash('Erreur: Cette immatriculation existe déjà!', 'error')

    return render_template('ajouter_voiture.html')

@app.route('/voiture/modifier/<int:id>', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent modifier des voitures
def modifier_voiture(id):
    voiture = Voiture.query.get_or_404(id)

    if request.method == 'POST':
        voiture.nom = request.form['nom']
        voiture.immatriculation = request.form['immatriculation']
        voiture.couleur = request.form['couleur']
        voiture.km = int(request.form['km'])
        voiture.carburant = request.form['carburant']
        voiture.disponible = 'disponible' in request.form

        try:
            db.session.commit()
            flash('Voiture modifiée avec succès!', 'success')
            return redirect(url_for('voitures'))
        except:
            flash('Erreur lors de la modification!', 'error')

    return render_template('modifier_voiture.html', voiture=voiture)

@app.route('/voiture/supprimer/<int:id>')
@admin_required  # Seuls les admins peuvent supprimer des voitures
def supprimer_voiture(id):
    voiture = Voiture.query.get_or_404(id)

    try:
        db.session.delete(voiture)
        db.session.commit()
        flash('Voiture supprimée avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')

    return redirect(url_for('voitures'))

# Routes pour les réservations
@app.route('/reservations')
@admin_required  # Seuls les admins peuvent gérer les réservations
def reservations():
    reservations = Reservation.query.all()
    return render_template('reservations.html', reservations=reservations)

@app.route('/reservation/ajouter', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent ajouter des réservations
def ajouter_reservation():
    if request.method == 'POST':
        nom_client = request.form['nom_client']
        date_depart = datetime.strptime(request.form['date_depart'], '%Y-%m-%d').date()
        date_retour = datetime.strptime(request.form['date_retour'], '%Y-%m-%d').date()
        prix_par_jour = float(request.form['prix_par_jour'])
        voiture_id = int(request.form['voiture_id'])

        # Calculer le nombre de jours
        jours = (date_retour - date_depart).days
        if jours <= 0:
            flash('La date de retour doit être après la date de départ!', 'error')
            voitures = Voiture.query.filter_by(disponible=True).all()
            return render_template('ajouter_reservation.html', voitures=voitures)

        # Calculer le total
        total = jours * prix_par_jour

        nouvelle_reservation = Reservation(
            nom_client=nom_client,
            date_depart=date_depart,
            date_retour=date_retour,
            jours=jours,
            prix_par_jour=prix_par_jour,
            total=total,
            voiture_id=voiture_id
        )

        # Marquer la voiture comme indisponible
        voiture = Voiture.query.get(voiture_id)
        voiture.disponible = False

        try:
            db.session.add(nouvelle_reservation)
            db.session.flush()  # Pour obtenir l'ID de la réservation
            creer_transaction_reservation(nouvelle_reservation)
            db.session.commit()
            flash('Réservation ajoutée avec succès!', 'success')
            return redirect(url_for('reservations'))
        except:
            db.session.rollback()
            flash('Erreur lors de l\'ajout de la réservation!', 'error')

    voitures = Voiture.query.filter_by(disponible=True).all()
    return render_template('ajouter_reservation.html', voitures=voitures)

@app.route('/reservation/modifier/<int:id>', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent modifier des réservations
def modifier_reservation(id):
    reservation = Reservation.query.get_or_404(id)

    if request.method == 'POST':
        # Rendre l'ancienne voiture disponible
        ancienne_voiture = Voiture.query.get(reservation.voiture_id)
        ancienne_voiture.disponible = True

        reservation.nom_client = request.form['nom_client']
        reservation.date_depart = datetime.strptime(request.form['date_depart'], '%Y-%m-%d').date()
        reservation.date_retour = datetime.strptime(request.form['date_retour'], '%Y-%m-%d').date()
        reservation.prix_par_jour = float(request.form['prix_par_jour'])
        reservation.voiture_id = int(request.form['voiture_id'])

        # Recalculer
        reservation.jours = (reservation.date_retour - reservation.date_depart).days
        reservation.total = reservation.jours * reservation.prix_par_jour

        # Marquer la nouvelle voiture comme indisponible
        nouvelle_voiture = Voiture.query.get(reservation.voiture_id)
        nouvelle_voiture.disponible = False

        try:
            db.session.commit()
            flash('Réservation modifiée avec succès!', 'success')
            return redirect(url_for('reservations'))
        except:
            flash('Erreur lors de la modification!', 'error')

    voitures = Voiture.query.filter_by(disponible=True).all()
    voitures.append(reservation.voiture)  # Ajouter la voiture actuelle
    return render_template('modifier_reservation.html', reservation=reservation, voitures=voitures)

@app.route('/reservation/supprimer/<int:id>')
@admin_required  # Seuls les admins peuvent supprimer des réservations
def supprimer_reservation(id):
    reservation = Reservation.query.get_or_404(id)

    # Rendre la voiture disponible
    voiture = Voiture.query.get(reservation.voiture_id)
    voiture.disponible = True

    try:
        db.session.delete(reservation)
        db.session.commit()
        flash('Réservation supprimée avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')

    return redirect(url_for('reservations'))

@app.route('/reservation/recu/<int:id>')
@login_required
def generer_recu(id):
    reservation = Reservation.query.get_or_404(id)
    return render_template('recu.html', reservation=reservation)

@app.route('/reservation/recu_pdf/<int:id>')
@login_required
def generer_recu_pdf(id):
    reservation = Reservation.query.get_or_404(id)

    # Créer un buffer pour le PDF
    buffer = io.BytesIO()

    # Créer le PDF
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Essayer d'ajouter le logo
    logo_path = os.path.join('static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        try:
            p.drawImage(logo_path, 50, height - 80, width=100, height=40, preserveAspectRatio=True)
        except:
            pass  # Si erreur avec l'image, continuer sans logo

    # Titre
    p.setFont("Helvetica-Bold", 18)
    p.drawString(200, height - 50, "GOLD 7 CAR RENT")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, height - 70, "REÇU DE LOCATION DE VOITURE")

    # Informations de la réservation
    p.setFont("Helvetica", 12)
    y = height - 120

    p.drawString(50, y, f"Client: {reservation.nom_client}")
    y -= 20
    p.drawString(50, y, f"Voiture: {reservation.voiture.nom}")
    y -= 20
    p.drawString(50, y, f"Immatriculation: {reservation.voiture.immatriculation}")
    y -= 20
    p.drawString(50, y, f"Date de départ: {reservation.date_depart}")
    y -= 20
    p.drawString(50, y, f"Date de retour: {reservation.date_retour}")
    y -= 20
    p.drawString(50, y, f"Nombre de jours: {reservation.jours}")
    y -= 20
    p.drawString(50, y, f"Prix par jour: {reservation.prix_par_jour} DH")
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"TOTAL: {reservation.total} DH")

    p.showPage()
    p.save()

    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=recu_{reservation.id}.pdf'

    return response

# Routes pour les vidanges
@app.route('/vidanges')
@admin_required  # Seuls les admins peuvent gérer les vidanges
def vidanges():
    vidanges = Vidange.query.all()
    return render_template('vidanges.html', vidanges=vidanges)

@app.route('/vidange/ajouter', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent ajouter des vidanges
def ajouter_vidange():
    if request.method == 'POST':
        immatriculation = request.form['immatriculation']
        derniere_vidange = int(request.form['derniere_vidange'])
        voiture_id = int(request.form['voiture_id'])

        # Calculer la prochaine vidange
        prochaine_vidange = derniere_vidange + 10000

        nouvelle_vidange = Vidange(
            immatriculation=immatriculation,
            derniere_vidange=derniere_vidange,
            prochaine_vidange=prochaine_vidange,
            voiture_id=voiture_id
        )

        try:
            db.session.add(nouvelle_vidange)
            db.session.commit()
            flash('Vidange ajoutée avec succès!', 'success')
            return redirect(url_for('vidanges'))
        except:
            flash('Erreur lors de l\'ajout de la vidange!', 'error')

    voitures = Voiture.query.all()
    return render_template('ajouter_vidange.html', voitures=voitures)

@app.route('/vidange/modifier/<int:id>', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent modifier des vidanges
def modifier_vidange(id):
    vidange = Vidange.query.get_or_404(id)

    if request.method == 'POST':
        vidange.immatriculation = request.form['immatriculation']
        vidange.derniere_vidange = int(request.form['derniere_vidange'])
        vidange.voiture_id = int(request.form['voiture_id'])

        # Recalculer la prochaine vidange
        vidange.prochaine_vidange = vidange.derniere_vidange + 10000

        try:
            db.session.commit()
            flash('Vidange modifiée avec succès!', 'success')
            return redirect(url_for('vidanges'))
        except:
            flash('Erreur lors de la modification!', 'error')

    voitures = Voiture.query.all()
    return render_template('modifier_vidange.html', vidange=vidange, voitures=voitures)

@app.route('/vidange/supprimer/<int:id>')
@admin_required  # Seuls les admins peuvent supprimer des vidanges
def supprimer_vidange(id):
    vidange = Vidange.query.get_or_404(id)

    try:
        db.session.delete(vidange)
        db.session.commit()
        flash('Vidange supprimée avec succès!', 'success')
    except:
        flash('Erreur lors de la suppression!', 'error')

    return redirect(url_for('vidanges'))

# Routes pour les retours
@app.route('/retours')
@admin_required  # Seuls les admins peuvent gérer les retours
def retours():
    retours = Retour.query.order_by(Retour.date_retour.desc(), Retour.heure_retour.desc()).all()
    today = date.today()
    return render_template('retours.html', retours=retours, today=today)

@app.route('/retour/ajouter', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent ajouter des retours
def ajouter_retour():
    if request.method == 'POST':
        date_retour = datetime.strptime(request.form['date_retour'], '%Y-%m-%d').date()
        heure_retour = datetime.strptime(request.form['heure_retour'], '%H:%M').time()
        nom_client = request.form['nom_client']
        voiture_id = int(request.form['voiture_id'])
        reservation_id = request.form.get('reservation_id')
        km_retour = request.form.get('km_retour')
        etat_vehicule = request.form.get('etat_vehicule', '')
        commentaires = request.form.get('commentaires', '')

        # Convertir reservation_id et km_retour en entiers si fournis
        reservation_id = int(reservation_id) if reservation_id else None
        km_retour = int(km_retour) if km_retour else None

        nouveau_retour = Retour(
            date_retour=date_retour,
            heure_retour=heure_retour,
            nom_client=nom_client,
            voiture_id=voiture_id,
            reservation_id=reservation_id,
            km_retour=km_retour,
            etat_vehicule=etat_vehicule,
            commentaires=commentaires
        )

        # Marquer la voiture comme disponible
        voiture = Voiture.query.get(voiture_id)
        voiture.disponible = True

        # Mettre à jour le kilométrage de la voiture si fourni
        if km_retour:
            voiture.km = km_retour

        try:
            db.session.add(nouveau_retour)
            db.session.commit()
            flash('Retour enregistré avec succès!', 'success')
            return redirect(url_for('retours'))
        except:
            flash('Erreur lors de l\'enregistrement du retour!', 'error')

    # Récupérer les voitures indisponibles (en location) et les réservations actives
    voitures_en_location = Voiture.query.filter_by(disponible=False).all()
    reservations_actives = Reservation.query.join(Voiture).filter(Voiture.disponible == False).all()
    today = date.today()
    now = datetime.now()

    return render_template('ajouter_retour.html',
                         voitures=voitures_en_location,
                         reservations=reservations_actives,
                         today=today,
                         now=now)

@app.route('/retour/modifier/<int:id>', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent modifier des retours
def modifier_retour(id):
    retour = Retour.query.get_or_404(id)

    if request.method == 'POST':
        retour.date_retour = datetime.strptime(request.form['date_retour'], '%Y-%m-%d').date()
        retour.heure_retour = datetime.strptime(request.form['heure_retour'], '%H:%M').time()
        retour.nom_client = request.form['nom_client']
        retour.voiture_id = int(request.form['voiture_id'])
        retour.reservation_id = request.form.get('reservation_id')
        retour.km_retour = request.form.get('km_retour')
        retour.etat_vehicule = request.form.get('etat_vehicule', '')
        retour.commentaires = request.form.get('commentaires', '')

        # Convertir en entiers si fournis
        retour.reservation_id = int(retour.reservation_id) if retour.reservation_id else None
        retour.km_retour = int(retour.km_retour) if retour.km_retour else None

        # Mettre à jour le kilométrage de la voiture si fourni
        if retour.km_retour:
            voiture = Voiture.query.get(retour.voiture_id)
            voiture.km = retour.km_retour

        try:
            db.session.commit()
            flash('Retour modifié avec succès!', 'success')
            return redirect(url_for('retours'))
        except:
            flash('Erreur lors de la modification!', 'error')

    voitures = Voiture.query.all()
    reservations = Reservation.query.all()
    return render_template('modifier_retour.html', retour=retour, voitures=voitures, reservations=reservations)

@app.route('/retour/supprimer/<int:id>')
@admin_required  # Seuls les admins peuvent supprimer des retours
def supprimer_retour(id):
    retour = Retour.query.get_or_404(id)

    try:
        db.session.delete(retour)
        db.session.commit()
        flash('Retour supprimé avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')

    return redirect(url_for('retours'))

# Routes pour la comptabilité
@app.route('/comptabilite')
@admin_required  # Seuls les admins peuvent accéder à la comptabilité
def comptabilite():
    # Récupérer les données financières
    reservations = Reservation.query.all()
    depenses = Depense.query.all()
    transactions = Transaction.query.order_by(Transaction.date_transaction.desc()).limit(10).all()

    # Calculer les totaux
    total_recettes = sum(r.total for r in reservations)
    total_depenses = sum(d.montant for d in depenses)
    benefice = total_recettes - total_depenses

    # Statistiques par mois (3 derniers mois)
    from datetime import datetime, timedelta
    today = date.today()
    trois_mois = today - timedelta(days=90)

    recettes_recentes = Reservation.query.filter(Reservation.date_creation >= trois_mois).all()
    depenses_recentes = Depense.query.filter(Depense.date_creation >= trois_mois).all()

    # Statistiques par catégorie
    categories = CategorieDepense.query.all()
    stats_categories = []
    for cat in categories:
        total_cat = sum(d.montant for d in cat.depenses)
        if total_cat > 0:
            stats_categories.append({
                'nom': cat.nom,
                'total': total_cat,
                'couleur': cat.couleur,
                'count': len(cat.depenses)
            })

    return render_template('comptabilite.html',
                         total_recettes=total_recettes,
                         total_depenses=total_depenses,
                         benefice=benefice,
                         transactions=transactions,
                         stats_categories=stats_categories,
                         recettes_recentes=recettes_recentes,
                         depenses_recentes=depenses_recentes)

@app.route('/comptabilite/depenses')
@login_required
def depenses():
    depenses = Depense.query.order_by(Depense.date_depense.desc()).all()
    categories = CategorieDepense.query.all()
    today = date.today()
    return render_template('depenses.html', depenses=depenses, categories=categories, today=today)

@app.route('/comptabilite/depense/ajouter', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent ajouter des dépenses
def ajouter_depense():
    if request.method == 'POST':
        description = request.form['description']
        montant = float(request.form['montant'])
        date_depense = datetime.strptime(request.form['date_depense'], '%Y-%m-%d').date()
        categorie_id = int(request.form['categorie_id'])
        voiture_id = request.form.get('voiture_id')
        facture_numero = request.form.get('facture_numero', '')
        fournisseur = request.form.get('fournisseur', '')
        commentaires = request.form.get('commentaires', '')
        mode_paiement = request.form.get('mode_paiement', '')

        voiture_id = int(voiture_id) if voiture_id else None

        nouvelle_depense = Depense(
            description=description,
            montant=montant,
            date_depense=date_depense,
            categorie_id=categorie_id,
            voiture_id=voiture_id,
            facture_numero=facture_numero,
            fournisseur=fournisseur,
            commentaires=commentaires
        )

        # Créer la transaction correspondante
        nouvelle_transaction = Transaction(
            type_transaction='depense',
            description=f"Dépense: {description}",
            montant=montant,
            date_transaction=date_depense,
            depense_id=None,  # Sera mis à jour après l'ajout de la dépense
            mode_paiement=mode_paiement
        )

        try:
            db.session.add(nouvelle_depense)
            db.session.flush()  # Pour obtenir l'ID de la dépense
            nouvelle_transaction.depense_id = nouvelle_depense.id
            db.session.add(nouvelle_transaction)
            db.session.commit()
            flash('Dépense ajoutée avec succès!', 'success')
            return redirect(url_for('depenses'))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de l\'ajout de la dépense!', 'error')

    categories = CategorieDepense.query.all()
    voitures = Voiture.query.all()
    today = date.today()
    return render_template('ajouter_depense.html', categories=categories, voitures=voitures, today=today)

@app.route('/comptabilite/depense/modifier/<int:id>', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent modifier des dépenses
def modifier_depense(id):
    depense = Depense.query.get_or_404(id)

    if request.method == 'POST':
        depense.description = request.form['description']
        depense.montant = float(request.form['montant'])
        depense.date_depense = datetime.strptime(request.form['date_depense'], '%Y-%m-%d').date()
        depense.categorie_id = int(request.form['categorie_id'])
        depense.voiture_id = request.form.get('voiture_id')
        depense.facture_numero = request.form.get('facture_numero', '')
        depense.fournisseur = request.form.get('fournisseur', '')
        depense.commentaires = request.form.get('commentaires', '')

        depense.voiture_id = int(depense.voiture_id) if depense.voiture_id else None

        # Mettre à jour la transaction correspondante
        if depense.transaction:
            depense.transaction.description = f"Dépense: {depense.description}"
            depense.transaction.montant = depense.montant
            depense.transaction.date_transaction = depense.date_depense

        try:
            db.session.commit()
            flash('Dépense modifiée avec succès!', 'success')
            return redirect(url_for('depenses'))
        except:
            flash('Erreur lors de la modification!', 'error')

    categories = CategorieDepense.query.all()
    voitures = Voiture.query.all()
    return render_template('modifier_depense.html', depense=depense, categories=categories, voitures=voitures)

@app.route('/comptabilite/depense/supprimer/<int:id>')
@admin_required  # Seuls les admins peuvent supprimer des dépenses
def supprimer_depense(id):
    depense = Depense.query.get_or_404(id)

    try:
        # Supprimer la transaction associée
        if depense.transaction:
            db.session.delete(depense.transaction)
        db.session.delete(depense)
        db.session.commit()
        flash('Dépense supprimée avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')

    return redirect(url_for('depenses'))

@app.route('/comptabilite/categories')
@login_required
def categories_depenses():
    categories = CategorieDepense.query.all()
    return render_template('categories_depenses.html', categories=categories)

@app.route('/comptabilite/categorie/ajouter', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent ajouter des catégories
def ajouter_categorie():
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form.get('description', '')
        couleur = request.form.get('couleur', '#6c757d')

        nouvelle_categorie = CategorieDepense(
            nom=nom,
            description=description,
            couleur=couleur
        )

        try:
            db.session.add(nouvelle_categorie)
            db.session.commit()
            flash('Catégorie ajoutée avec succès!', 'success')
            return redirect(url_for('categories_depenses'))
        except:
            flash('Erreur: Cette catégorie existe déjà!', 'error')

    return render_template('ajouter_categorie.html')

@app.route('/comptabilite/categorie/modifier/<int:id>', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent modifier des catégories
def modifier_categorie(id):
    categorie = CategorieDepense.query.get_or_404(id)

    if request.method == 'POST':
        categorie.nom = request.form['nom']
        categorie.description = request.form.get('description', '')
        categorie.couleur = request.form.get('couleur', '#6c757d')

        try:
            db.session.commit()
            flash('Catégorie modifiée avec succès!', 'success')
            return redirect(url_for('categories_depenses'))
        except:
            flash('Erreur: Ce nom de catégorie existe déjà!', 'error')

    return render_template('modifier_categorie.html', categorie=categorie)

@app.route('/comptabilite/categorie/supprimer/<int:id>')
@admin_required  # Seuls les admins peuvent supprimer des catégories
def supprimer_categorie(id):
    categorie = CategorieDepense.query.get_or_404(id)

    # Vérifier s'il y a des dépenses associées
    if categorie.depenses:
        flash(f'Impossible de supprimer la catégorie "{categorie.nom}" car elle contient {len(categorie.depenses)} dépense(s).', 'error')
        return redirect(url_for('categories_depenses'))

    try:
        db.session.delete(categorie)
        db.session.commit()
        flash('Catégorie supprimée avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')

    return redirect(url_for('categories_depenses'))

@app.route('/comptabilite/rapport')
@login_required
def rapport_financier():
    # Paramètres de date
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')

    if not date_debut:
        date_debut = date.today().replace(day=1)  # Premier jour du mois
    else:
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()

    if not date_fin:
        date_fin = date.today()
    else:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()

    # Récupérer les données pour la période
    reservations = Reservation.query.filter(
        Reservation.date_creation >= date_debut,
        Reservation.date_creation <= date_fin
    ).all()

    depenses = Depense.query.filter(
        Depense.date_depense >= date_debut,
        Depense.date_depense <= date_fin
    ).all()

    # Calculer les totaux
    total_recettes = sum(r.total for r in reservations)
    total_depenses = sum(d.montant for d in depenses)
    benefice = total_recettes - total_depenses

    # Grouper les dépenses par catégorie
    depenses_par_categorie = {}
    for depense in depenses:
        cat_nom = depense.categorie.nom
        if cat_nom not in depenses_par_categorie:
            depenses_par_categorie[cat_nom] = {
                'total': 0,
                'count': 0,
                'couleur': depense.categorie.couleur
            }
        depenses_par_categorie[cat_nom]['total'] += depense.montant
        depenses_par_categorie[cat_nom]['count'] += 1

    return render_template('rapport_financier.html',
                         date_debut=date_debut,
                         date_fin=date_fin,
                         reservations=reservations,
                         depenses=depenses,
                         total_recettes=total_recettes,
                         total_depenses=total_depenses,
                         benefice=benefice,
                         depenses_par_categorie=depenses_par_categorie)

# Route pour servir les fichiers uploadés
@app.route('/uploads/clients/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Routes pour les clients
@app.route('/clients')
@admin_required  # Seuls les admins peuvent gérer les clients
def clients():
    clients = Client.query.order_by(Client.nom, Client.prenom).all()
    return render_template('clients.html', clients=clients)

@app.route('/client/<int:id>')
@login_required
def voir_client(id):
    client = Client.query.get_or_404(id)
    return render_template('voir_client.html', client=client)

@app.route('/client/ajouter', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent ajouter des clients
def ajouter_client():
    if request.method == 'POST':
        # Informations personnelles
        nom = request.form['nom']
        prenom = request.form['prenom']
        date_naissance = datetime.strptime(request.form['date_naissance'], '%Y-%m-%d').date()
        lieu_naissance = request.form.get('lieu_naissance', '')
        nationalite = request.form.get('nationalite', 'Marocaine')
        sexe = request.form.get('sexe', '')

        # Coordonnées
        telephone = request.form['telephone']
        email = request.form.get('email', '')
        adresse = request.form['adresse']
        ville = request.form['ville']
        code_postal = request.form.get('code_postal', '')
        pays = request.form.get('pays', 'Maroc')

        # Documents d'identité
        type_piece_identite = request.form['type_piece_identite']
        numero_piece_identite = request.form['numero_piece_identite']
        date_expiration_piece = request.form.get('date_expiration_piece')
        if date_expiration_piece:
            date_expiration_piece = datetime.strptime(date_expiration_piece, '%Y-%m-%d').date()
        else:
            date_expiration_piece = None

        # Permis de conduire
        numero_permis = request.form['numero_permis']
        date_obtention_permis = datetime.strptime(request.form['date_obtention_permis'], '%Y-%m-%d').date()
        date_expiration_permis = datetime.strptime(request.form['date_expiration_permis'], '%Y-%m-%d').date()
        categorie_permis = request.form.get('categorie_permis', 'B')
        pays_delivrance_permis = request.form.get('pays_delivrance_permis', 'Maroc')

        # Informations complémentaires
        profession = request.form.get('profession', '')
        entreprise = request.form.get('entreprise', '')
        personne_contact_urgence = request.form.get('personne_contact_urgence', '')
        telephone_urgence = request.form.get('telephone_urgence', '')
        notes = request.form.get('notes', '')

        # Gestion des fichiers uploadés
        photo_piece_identite = None
        photo_permis = None

        if 'photo_piece_identite' in request.files:
            file = request.files['photo_piece_identite']
            if file.filename != '':
                photo_piece_identite = save_uploaded_file(file, f'piece_{numero_piece_identite}')

        if 'photo_permis' in request.files:
            file = request.files['photo_permis']
            if file.filename != '':
                photo_permis = save_uploaded_file(file, f'permis_{numero_permis}')

        nouveau_client = Client(
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            lieu_naissance=lieu_naissance,
            nationalite=nationalite,
            sexe=sexe,
            telephone=telephone,
            email=email,
            adresse=adresse,
            ville=ville,
            code_postal=code_postal,
            pays=pays,
            type_piece_identite=type_piece_identite,
            numero_piece_identite=numero_piece_identite,
            date_expiration_piece=date_expiration_piece,
            photo_piece_identite=photo_piece_identite,
            numero_permis=numero_permis,
            date_obtention_permis=date_obtention_permis,
            date_expiration_permis=date_expiration_permis,
            categorie_permis=categorie_permis,
            pays_delivrance_permis=pays_delivrance_permis,
            photo_permis=photo_permis,
            profession=profession,
            entreprise=entreprise,
            personne_contact_urgence=personne_contact_urgence,
            telephone_urgence=telephone_urgence,
            notes=notes
        )

        try:
            db.session.add(nouveau_client)
            db.session.commit()
            flash('Client ajouté avec succès!', 'success')
            return redirect(url_for('clients'))
        except Exception as e:
            db.session.rollback()
            # Supprimer les fichiers uploadés en cas d'erreur
            if photo_piece_identite:
                delete_file(photo_piece_identite)
            if photo_permis:
                delete_file(photo_permis)
            flash('Erreur: Ce numéro de pièce d\'identité ou de permis existe déjà!', 'error')

    return render_template('ajouter_client.html')

@app.route('/client/modifier/<int:id>', methods=['GET', 'POST'])
@admin_required  # Seuls les admins peuvent modifier des clients
def modifier_client(id):
    client = Client.query.get_or_404(id)

    if request.method == 'POST':
        # Sauvegarder les anciens fichiers pour suppression si nécessaire
        ancien_photo_piece = client.photo_piece_identite
        ancien_photo_permis = client.photo_permis

        # Mettre à jour les informations
        client.nom = request.form['nom']
        client.prenom = request.form['prenom']
        client.date_naissance = datetime.strptime(request.form['date_naissance'], '%Y-%m-%d').date()
        client.lieu_naissance = request.form.get('lieu_naissance', '')
        client.nationalite = request.form.get('nationalite', 'Marocaine')
        client.sexe = request.form.get('sexe', '')
        client.telephone = request.form['telephone']
        client.email = request.form.get('email', '')
        client.adresse = request.form['adresse']
        client.ville = request.form['ville']
        client.code_postal = request.form.get('code_postal', '')
        client.pays = request.form.get('pays', 'Maroc')
        client.type_piece_identite = request.form['type_piece_identite']
        client.numero_piece_identite = request.form['numero_piece_identite']

        date_expiration_piece = request.form.get('date_expiration_piece')
        if date_expiration_piece:
            client.date_expiration_piece = datetime.strptime(date_expiration_piece, '%Y-%m-%d').date()
        else:
            client.date_expiration_piece = None

        client.numero_permis = request.form['numero_permis']
        client.date_obtention_permis = datetime.strptime(request.form['date_obtention_permis'], '%Y-%m-%d').date()
        client.date_expiration_permis = datetime.strptime(request.form['date_expiration_permis'], '%Y-%m-%d').date()
        client.categorie_permis = request.form.get('categorie_permis', 'B')
        client.pays_delivrance_permis = request.form.get('pays_delivrance_permis', 'Maroc')
        client.profession = request.form.get('profession', '')
        client.entreprise = request.form.get('entreprise', '')
        client.personne_contact_urgence = request.form.get('personne_contact_urgence', '')
        client.telephone_urgence = request.form.get('telephone_urgence', '')
        client.notes = request.form.get('notes', '')
        client.statut = request.form.get('statut', 'actif')

        # Gestion des nouveaux fichiers
        if 'photo_piece_identite' in request.files:
            file = request.files['photo_piece_identite']
            if file.filename != '':
                nouveau_fichier = save_uploaded_file(file, f'piece_{client.numero_piece_identite}')
                if nouveau_fichier:
                    if ancien_photo_piece:
                        delete_file(ancien_photo_piece)
                    client.photo_piece_identite = nouveau_fichier

        if 'photo_permis' in request.files:
            file = request.files['photo_permis']
            if file.filename != '':
                nouveau_fichier = save_uploaded_file(file, f'permis_{client.numero_permis}')
                if nouveau_fichier:
                    if ancien_photo_permis:
                        delete_file(ancien_photo_permis)
                    client.photo_permis = nouveau_fichier

        try:
            db.session.commit()
            flash('Client modifié avec succès!', 'success')
            return redirect(url_for('clients'))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la modification!', 'error')

    return render_template('modifier_client.html', client=client)

@app.route('/client/supprimer/<int:id>')
@admin_required  # Seuls les admins peuvent supprimer des clients
def supprimer_client(id):
    client = Client.query.get_or_404(id)

    # Vérifier s'il y a des réservations associées (par nom complet)
    try:
        reservations_count = Reservation.query.filter_by(nom_client=client.nom_complet).count()
        if reservations_count > 0:
            flash(f'Impossible de supprimer le client "{client.nom_complet}" car il a {reservations_count} réservation(s).', 'error')
            return redirect(url_for('clients'))
    except Exception as e:
        # Si erreur dans la vérification, on continue quand même
        print(f"Erreur vérification réservations: {e}")

    # Supprimer les fichiers associés (de manière sécurisée)
    try:
        if hasattr(client, 'photo_piece_identite') and client.photo_piece_identite:
            delete_file(client.photo_piece_identite)
    except Exception as e:
        print(f"Erreur suppression photo pièce identité: {e}")

    try:
        if hasattr(client, 'photo_permis') and client.photo_permis:
            delete_file(client.photo_permis)
    except Exception as e:
        print(f"Erreur suppression photo permis: {e}")

    # Supprimer le client de la base de données
    try:
        nom_client = client.nom_complet  # Sauvegarder le nom avant suppression
        db.session.delete(client)
        db.session.commit()
        flash(f'Client "{nom_client}" supprimé avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression du client: {str(e)}', 'error')

    return redirect(url_for('clients'))

# Fonction pour créer automatiquement les transactions lors des réservations
def creer_transaction_reservation(reservation):
    """Créer une transaction de recette pour une réservation"""
    transaction = Transaction(
        type_transaction='recette',
        description=f"Location - {reservation.nom_client}",
        montant=reservation.total,
        date_transaction=reservation.date_creation.date(),
        reservation_id=reservation.id,
        mode_paiement='Non spécifié'
    )
    db.session.add(transaction)

def corriger_transactions_manquantes():
    """Créer les transactions manquantes pour les dépenses existantes"""
    depenses_sans_transaction = Depense.query.filter(~Depense.id.in_(
        db.session.query(Transaction.depense_id).filter(Transaction.depense_id.isnot(None))
    )).all()

    for depense in depenses_sans_transaction:
        transaction = Transaction(
            type_transaction='depense',
            description=f"Dépense: {depense.description}",
            montant=depense.montant,
            date_transaction=depense.date_depense,
            depense_id=depense.id,
            mode_paiement='Non spécifié'
        )
        db.session.add(transaction)

    if depenses_sans_transaction:
        try:
            db.session.commit()
            print(f"Transactions créées pour {len(depenses_sans_transaction)} dépense(s) existante(s).")
        except:
            db.session.rollback()
            print("Erreur lors de la création des transactions manquantes.")

# Fonction pour initialiser les données de base
def initialiser_donnees_base():
    """Créer les catégories de dépenses par défaut si elles n'existent pas"""
    categories_defaut = [
        {'nom': 'Carburant', 'description': 'Essence, diesel et autres carburants', 'couleur': '#dc3545'},
        {'nom': 'Réparations', 'description': 'Réparations et maintenance des véhicules', 'couleur': '#fd7e14'},
        {'nom': 'Assurance', 'description': 'Assurances véhicules et responsabilité', 'couleur': '#20c997'},
        {'nom': 'Pièces détachées', 'description': 'Achat de pièces de rechange', 'couleur': '#6f42c1'},
        {'nom': 'Contrôle technique', 'description': 'Contrôles techniques obligatoires', 'couleur': '#0dcaf0'},
        {'nom': 'Nettoyage', 'description': 'Lavage et nettoyage des véhicules', 'couleur': '#198754'},
        {'nom': 'Frais administratifs', 'description': 'Paperasserie et frais divers', 'couleur': '#6c757d'},
    ]

    for cat_data in categories_defaut:
        # Vérifier si la catégorie existe déjà
        categorie_existante = CategorieDepense.query.filter_by(nom=cat_data['nom']).first()
        if not categorie_existante:
            nouvelle_categorie = CategorieDepense(
                nom=cat_data['nom'],
                description=cat_data['description'],
                couleur=cat_data['couleur']
            )
            db.session.add(nouvelle_categorie)

    try:
        db.session.commit()
        print("Catégories de dépenses par défaut créées avec succès!")
    except:
        db.session.rollback()
        print("Les catégories de dépenses existent déjà.")

if __name__ == '__main__':
    with app.app_context():
        init_database()
        initialiser_donnees_base()
        corriger_transactions_manquantes()

    # Configuration pour l'hébergement
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'

    app.run(debug=debug, host='0.0.0.0', port=port)

# Initialiser la base de données au démarrage de l'application
with app.app_context():
    init_database()
