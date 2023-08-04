from flask import Flask, jsonify, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField, PasswordField
from wtforms.validators import DataRequired
import random
import json
from pprint import pprint
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from functools import wraps
import os
from flask_migrate import Migrate
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sqlite:///cafes.db')

# Use Heroku Config Var for Database URL
# if 'DATABASE_URL' in os.environ:
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# else:
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cafes.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user' or 'admin'

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    cafes = relationship("Cafe", back_populates="author")


# Café TABLE Configuration
class Cafe(db.Model):
    __tablename__ = 'cafe'
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # Create reference to the User object, the "cafes" refers to the cafes property in the User class.
    author = relationship("User", back_populates="cafes")

    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column,
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        # return dictionary

        # Method 2. Alternatively, use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# Define the Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')


# Define the Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SearchCafeForm(FlaskForm):
    loc = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UpdateCafePriceForm(FlaskForm):
    new_price = StringField('New Price:', validators=[DataRequired()])
    submit = SubmitField('Update Price')


class AddCafeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    map_url = StringField('Map URL', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired()])
    loc = StringField('Location', validators=[DataRequired()])
    seats = StringField('Seats', validators=[DataRequired()])
    toilet = BooleanField('Has Toilet')
    wifi = BooleanField('Has WiFi')
    sockets = BooleanField('Has Sockets')
    calls = BooleanField('Can Take Calls')
    coffee_price = StringField('Coffee Price')
    submit = SubmitField('Submit')


class DeleteCafeForm(FlaskForm):
    id = IntegerField('Cafe\'s ID to Delete:', validators=[DataRequired()])
    submit = SubmitField('Delete Cafe')


with app.app_context():
    # Create all database tables
    db.create_all()

    # Retrieve all cafés from the database
    cafes = Cafe.query.all()

    # Get all cafés from our cafe.db into a dictionary, using a List Comprehension
    cafes_data = [cafe.to_dict() for cafe in cafes]

    # Get a random café from our cafe.db
    # Simply convert the random_cafe data record to a dictionary of key-value pairs.
    random_cafe = random.choice(cafes).to_dict()


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('assets/images/favicon.ico')


@app.route('/')
def home():
    pprint('Siisi Chacal ¡!¡')
    if cafes:
        # print(json.dumps({"All cafés": cafes_data}, indent=4))  # Print the JSON result
        # return jsonify(a_random_cafe=random_cafe_, cafes=cafes_data)
        return render_template('index.html', cafes=cafes_data)
    else:
        return jsonify({'message': 'No cafes found.'})


@app.route('/cafe/<int:cafe_id>')
def cafe_detail(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    print(json.dumps({"Cafes": cafe.to_dict()}, indent=4))  # Print the JSON result
    return render_template('cafe_detail.html', cafe=cafe, cafes=cafes_data)


@app.route('/random')
def get_random_cafe():
    if cafes:
        random_cafe_ = random.choice(cafes_data)
        print(json.dumps({"Random cafe": random_cafe_}, indent=4))  # Print the JSON result
        # return jsonify(cafe=random_cafe_)
        return render_template('random_cafe.html', random_cafe=random_cafe_)
    else:
        return jsonify({'message': 'No cafes found.'})


@app.route('/search', methods=['GET', 'POST'])
def search_cafes_by_location():
    form = SearchCafeForm()

    if request.method == 'POST':
        # Handle the POST request as before (search for cafés by location)
        query_location = request.form.get("loc")
        cafes_at_location = Cafe.query.filter_by(location=query_location).all()

        if cafes_at_location:
            cafes_at_location_data = [cafe.to_dict() for cafe in cafes_at_location]
            print(json.dumps({"Cafe by location": cafes_at_location_data}, indent=4))  # Print the JSON result
            return render_template('search.html', cafes_by_location=cafes_at_location_data, form=form)
        else:
            return jsonify(error={"Not Found": f"Sorry, we don't have cafes in that location: '{query_location}'."})
    else:
        # Handle the GET request (display the search form)
        return render_template('search.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if the username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify(error='Username already exists. Please choose a different username.'), 400

        # Create a new User object
        new_user = User(username=username, password=password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Automatically log in the newly registered user
        login_user(new_user)

        # Redirect the user to the home page after successful registration
        return redirect(url_for('home'))

    # If it's a GET request or the form is not valid, simply render the registration form
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error_message = None

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check the user's credentials (replace this with your actual authentication logic)
        if username == 'Requin' and password == '123' or username == 'Caouu' and password == 'abc':
            # Load the user object (you may fetch the user from the database based on the username)
            user = User.query.filter_by(username=username).first()
            print(f'Username: {username}\nPassword: {password}')
            if user:
                # Login the user and create a session
                login_user(user)
                # Redirect the user to the page they were trying to access before the login
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                error_message = 'Invalid username or password.'  # Set the error message for unsuccessful login
                print(error_message)
        else:
            error_message = 'Invalid username or password.'  # Set the error message for unsuccessful login
            print(error_message)

    # If it's a GET request or the login is not successful, render the login page with the error message
    return render_template('login.html', form=form, error_message=error_message)


@app.route('/logout')
def logout():
    logout_user()
    print('Allah Bless You ¡!¡')
    return redirect(url_for('home'))


#def is_admin():
#    """Check if the current user is an admin."""
#    if current_user.is_authenticated and current_user.role == 'admin':
#        return True
#    return False
#
#
#def admin_required(f):
#    """Decorator to restrict access to admin-only routes."""
#    @wraps(f)
#    def decorated_function(*args, **kwargs):
#        if not current_user.is_authenticated or current_user.role != 'admin':
#            # Redirect non-authenticated users to the login page
#            #return redirect(url_for('login', next=request.url))
#            return abort(403)
#        return f(*args, **kwargs)
#    return decorated_function
#


# Create admin-only decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 or 2, then return abort with 403 error
        if current_user.id != 1 and current_user.id != 2:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


@app.route('/add', methods=['GET', 'POST'])
# Mark with decorator
@admin_required
def add_new_cafe():
    form = AddCafeForm()
    if form.validate_on_submit():
        # Check if a café with the same name already exists
        existing_cafe = Cafe.query.filter_by(name=form.name.data).first()
        if existing_cafe:
            return jsonify(error='A cafe with that name already exists. Please choose a different name.'), 400

        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.loc.data,
            has_sockets=form.sockets.data,
            has_toilet=form.toilet.data,
            has_wifi=form.wifi.data,
            can_take_calls=form.calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response=[f"The {new_cafe.name} Cafe has been successfully added into the database."])

    return render_template('add_cafe.html', form=form)


@app.route('/choose-cafe', methods=['GET'])
def choose_cafe():
    return render_template('choose_cafe.html', cafes=cafes)


@app.route('/update-price/<int:cafe_id>', methods=['GET', 'POST', 'PATCH'])
# Mark with decorator
@admin_required
def update_cafe_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    form = UpdateCafePriceForm()

    if request.method == 'POST' and form.validate_on_submit():
        new_price = form.new_price.data
        cafe.coffee_price = new_price
        db.session.commit()
        pprint({"success": f"Coffee Price Successfully Updated To {cafe.coffee_price},\n For {cafe.name}."})

    elif request.method == 'PATCH':
        new_price = request.form.get('new_price')
        if cafe and new_price:
            cafe.coffee_price = new_price
            db.session.commit()
            # For GET requests or unsuccessful form submissions, simply render the template with the form
    return render_template('update_price.html', cafe=cafe, form=form)


@app.route('/delete-cafe', methods=['GET', 'POST'])
# Mark with decorator
@admin_required
def delete_cafe():
    form = DeleteCafeForm()
    if request.method == 'POST' and form.validate_on_submit():
        cafe_id = form.id.data  # Get the cafe_id from the submitted form
        cafe = Cafe.query.get(cafe_id)

        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify({"success": f'The {cafe.name} cafe has been successfully deleted from the database.'}), 200
        else:
            return jsonify({"error": f"Cafe with ID {cafe_id} not found in the database."}), 404

    return render_template('delete.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
