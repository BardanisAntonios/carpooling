import requests
from geopy.geocoders import Nominatim
from flask import Flask, render_template, url_for, flash, redirect, request, abort
from models import db, User, Route
from forms import RegistrationForm, LoginForm, RouteForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'unipi_secret_key_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carpooling.db'

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ΑΛΓΟΡΙΘΜΙΚΗ ΔΙΑΔΙΚΑΣΙΑ (Υπολογισμός CO2 & Κόστους) ---
def get_real_route_data(start_name, end_name):
    try:
        # Προσθέτουμε timeout 10 δευτερόλεπτα και ένα τυχαίο email στο user_agent
        geolocator = Nominatim(user_agent="unipi_student_project_p21110@unipi.gr", timeout=10)
        
        location_start = geolocator.geocode(start_name)
        location_end = geolocator.geocode(end_name)

        # Debugging: Εκτύπωση στο τερματικό για να βλέπουμε τι συμβαίνει
        print(f"Start: {location_start}")
        print(f"End: {location_end}")

        if not location_start or not location_end:
            return None

        # Routing API (OSRM)
        url = f"http://router.project-osrm.org/route/v1/driving/{location_start.longitude},{location_start.latitude};{location_end.longitude},{location_end.latitude}?overview=false"
        
        response = requests.get(url, timeout=10)
        route_data = response.json()

        if response.status_code != 200 or 'routes' not in route_data:
            return None

        distance_km = route_data['routes'][0]['distance'] / 1000
        duration_mins = route_data['routes'][0]['duration'] / 60

        return {
            "distance": round(distance_km, 1),
            "duration": round(duration_mins, 0),
            "co2": round(distance_km * 0.12, 2),
            "cost": round(distance_km * 0.15, 2)
        }
    except Exception as e:
        print(f"Σφάλμα API: {e}")
        return None

# --- ROUTES ---

@app.route("/")
def index():
    routes = Route.query.all()
    return render_template('index.html', routes=routes)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Επιτυχής εγγραφή!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Λάθος στοιχεία!', 'danger')
    return render_template('login.html', form=form)

@app.route("/route/new", methods=['GET', 'POST'])
@login_required
def create_route():
    form = RouteForm()
    if form.validate_on_submit():
        # Κλήση της αλγοριθμικής διαδικασίας με τα APIs
        api_results = get_real_route_data(form.start_point.data, form.end_point.data)
        
        if api_results:
            route = Route(
                start_point=form.start_point.data, 
                end_point=form.end_point.data, 
                departure_time=form.departure_time.data, 
                available_seats=form.seats.data, 
                distance_km=api_results['distance'],  
                driver=current_user
            )
            db.session.add(route)
            db.session.commit()
            
            flash(f"Η διαδρομή καταχωρήθηκε! Απόσταση: {api_results['distance']}km. "
                  f"Θα γλιτώσετε {api_results['co2']}kg CO2!", "success")
            return redirect(url_for('index'))
        else:
            flash("Δεν μπορέσαμε να βρούμε τις τοποθεσίες. Δοκιμάστε πιο συγκεκριμένες διευθύνσεις.", "danger")
            
    return render_template('create_route.html', form=form)

# Κράτηση θέσης
@app.route("/book_route/<int:route_id>")
@login_required
def book_route(route_id):
    route = Route.query.get_or_404(route_id)
    
    # Έλεγχος αν υπάρχουν διαθέσιμες θέσεις
    if route.available_seats > 0:
        # Έλεγχος αν ο οδηγός πάει να κλείσει θέση στον εαυτό του
        if route.driver_id == current_user.id:
            flash("Δεν μπορείτε να κλείσετε θέση στη δική σας διαδρομή!", "warning")
        else:
            route.available_seats -= 1  # Μειώνουμε τις θέσεις
            db.session.commit()
            flash(f"Η κράτηση για τη διαδρομή {route.start_point} -> {route.end_point} έγινε επιτυχώς!", "success")
    else:
        flash("Δεν υπάρχουν άλλες διαθέσιμες θέσεις σε αυτή τη διαδρομή.", "danger")
        
    return redirect(url_for('index'))

# --- ADMIN CRUD ---

@app.route("/admin/users")
@login_required
def admin_panel():
    if current_user.role != 'admin': abort(403)
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route("/admin/delete/<int:user_id>")
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    
    user_to_delete = User.query.get_or_404(user_id)
    
    if user_to_delete.id == current_user.id:
        flash('Δεν μπορείτε να διαγράψετε τον εαυτό σας!', 'danger')
        return redirect(url_for('admin_panel'))

    # --- Η ΔΙΟΡΘΩΣΗ: Διαγραφή των διαδρομών του χρήστη πριν τη διαγραφή του ίδιου ---
    Route.query.filter_by(driver_id=user_to_delete.id).delete()
    
    db.session.delete(user_to_delete)
    db.session.commit()
    
    flash(f'Ο χρήστης {user_to_delete.username} και οι διαδρομές του διαγράφηκαν.', 'success')
    return redirect(url_for('admin_panel'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Έλεγχος αν υπάρχει ήδη admin, αν όχι δημιούργησε έναν
        admin_exists = User.query.filter_by(role='admin').first()
        if not admin_exists:
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            default_admin = User(username='admin', email='admin@unipi.gr', 
                                 password=hashed_pw, role='admin')
            db.session.add(default_admin)
            db.session.commit()
            print("--- Ο Admin δημιουργήθηκε! User: admin@unipi.gr, Pass: admin123 ---")
            
    app.run(debug=True, port=5001)