from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, current_user, logout_user
from functools import wraps
import random
import json
import time
from datetime import datetime
from pprint import pprint
import os
from flask_sqlalchemy import SQLAlchemy
from forms import (RegistrationForm, LoginForm, SearchCafeForm,
                   UpdateCafePriceForm, AddCafeForm, DeleteCafeForm, DeleteUserForm)
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sqlite:///cafes.db')
app.config['WTF_CSRF_SECRET_KEY'] = app.config['SECRET_KEY']


# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cafes.db')

# For SQLite (comment out the PostgreSQL URI)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user' or 'admin'

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    cafes_ = relationship("Cafe", back_populates="author")


# Café TABLE Configuration
class Cafe(db.Model):
    __tablename__ = 'cafes'
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    # Create reference to the User object, the "cafés" refers to the cafés property in the User class.
    author = relationship("User", back_populates="cafes_")

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


with app.app_context():
    # Create all database tables
    db.create_all()

    migrate = Migrate(app, db)

    # Retrieve all cafés from the database
    cafes = Cafe.query.all()

    # Get all cafés from our cafe.db into a dictionary, using a List Comprehension
    cafes_data = [cafe.to_dict() for cafe in cafes]

    # Get a random café from our cafe.db
    # Simply convert the random_cafe data record to a dictionary of key-value pairs.
    #random_cafe = random.choice(cafes).to_dict()

    time_sec = time.localtime()
    current_year = time_sec.tm_year
    # getting the current date and time
    current_datetime = datetime.now()
    # getting the time from the current date and time in the given format
    current_time = current_datetime.strftime("%a %d %B")


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('assets/images/favicon.ico')


@app.route('/')
def home():
    pprint('Siisi Chacal ¡!¡')
    if cafes:
        # print(json.dumps({"All cafés": cafes_data}, indent=4))  # Print the JSON result
        # return jsonify(a_random_cafe=random_cafe_, cafes=cafes_data)
        return render_template('index.html', cafes=cafes_data, date=current_time, year=current_year)
    else:
        # Set the error message for unsuccessful search
        error_message = 'Sorry No Cafes found 😭 ¡!¡'
        print(error_message)
        return render_template('index.html', error_message=error_message, date=current_time, year=current_year)
        # return jsonify({'message': 'No cafes found.'})


@app.route('/cafe/<int:cafe_id>')
def cafe_detail(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    print(json.dumps({"Cafes 😎": cafe.to_dict()}, indent=4))  # Print the JSON result
    return render_template('cafe_detail.html', cafe=cafe, cafes=cafes_data, date=current_time, year=current_year)


@app.route('/random')
def get_random_cafe():
    if cafes:
        random_cafe_ = random.choice(cafes_data)
        print(json.dumps({"Random cafe 👌🏿": random_cafe_}, indent=4))  # Print the JSON result
        # return jsonify(cafe=random_cafe_)
        return render_template('random_cafe.html', random_cafe=random_cafe_, date=current_time, year=current_year)


@app.route('/search', methods=['GET', 'POST'])
def search_cafes_by_location():
    form = SearchCafeForm()
    error_message = None

    if request.method == 'POST':
        # Handle the POST request as before (search for cafés by location)
        query_location = request.form.get("loc")
        cafes_at_location = Cafe.query.filter_by(location=query_location).all()

        if cafes_at_location:
            cafes_at_location_data = [cafe.to_dict() for cafe in cafes_at_location]
            print(json.dumps({"Cafe by location 👍🏿": cafes_at_location_data}, indent=4))  # Print the JSON result
            return render_template('search.html', cafes_by_location=cafes_at_location_data, form=form,
                                   date=current_time, year=current_year)
        else:
            # Set the error message for unsuccessful search
            error_message = f"Sorry, we don't have cafes in that location: '😝 {query_location} 😭'."
            print(error_message)
            return render_template('search.html', form=form, error_message=error_message,
                                   date=current_time, year=current_year)
    else:
        # Handle the GET request (display the search form)
        return render_template('search.html', form=form, error_message=error_message,
                               date=current_time, year=current_year)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if the username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            # Set the error message for unsuccessful register
            error_message = f'Username already exists. Please choose a different one than 😭 {username} 😝. ¡!¡'
            print(error_message)
            return render_template('register.html', form=form, error_message=error_message,
                                   date=current_time, year=current_year)
            # return jsonify(error='Username already exists. Please choose a different username.'), 400

        # Create a new User object
        new_user = User(username=username, password=password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Automatically log in the newly registered user
        login_user(new_user)

        # Set the delete message for successful delete
        register_message = f'User: 👌🏿 {username} ¡!¡ {password} 💪🏿 has been successfully registered to the database ¡!¡'
        print(register_message)
        return render_template('register.html', form=form, register_message=register_message,
                               date=current_time, year=current_year)

    # If it's a GET request or the form is not valid, simply render the registration form
    return render_template('register.html', form=form, date=current_time, year=current_year)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error_message = None

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Load the user object (you may fetch the user from the database based on the username)
        user = User.query.filter_by(username=username).first()

        if not user:
            # Set the error message for unsuccessful login
            error_message = f'Invalid Name: 😭 {username} 😝.'
            print(error_message)
        elif user.password != password:
            # Set the error message for unsuccessful login
            error_message = f'Invalid Password: 😭 {password} 😝.'
            print(error_message)
            # If it's a GET request or the login is not successful, render the login page with the error message
            return render_template('login.html', form=form, error_message=error_message,
                                   date=current_time, year=current_year)
        else:
            print(f'Username: {username}\nPassword: {password}')
            # Login the user and create a session
            login_user(user)
            return redirect(url_for('home'))

    # If it's a GET request or the login is not successful, render the login page with the error message
    return render_template('login.html', form=form, error_message=error_message,
                           date=current_time, year=current_year)


@app.route('/logout')
def logout():
    logout_user()
    print('Allah Bless You ¡!¡')
    return redirect(url_for('home'))


# Create admin-only decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If a User is not an admin, then return abort with 403 error
        if current_user.role != 'admin':
            error_message = f'Sorry 😭 Only Admin Allowed ¡!¡ 😝.'
            print(error_message)

            # If it's a GET request or the login is not successful, render the login page with the error message
            return render_template('index.html', error_message=error_message,
                                   date=current_time, year=current_year)
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
            # Set the error message for unsuccessful register
            error_message = f'Cafe\'s Name already exists. Please choose a different one than 😭 {existing_cafe} 😝. ¡!¡'
            print(error_message)
            return render_template('add_cafe.html', form=form, error_message=error_message,
                                   date=current_time, year=current_year)

        new_cafe = Cafe(
            author_id=current_user.id,
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

        # Redirect to cafe_detail page for the newly added café
        return redirect(url_for('cafe_detail', cafe_id=new_cafe.id))

        # return jsonify(response=[f"The {new_cafe.name} Cafe has been successfully added into the database."])

    return render_template('add_cafe.html', form=form, date=current_time, year=current_year)


@app.route('/choose-cafe', methods=['GET'])
def choose_cafe():
    return render_template('choose_cafe.html', cafes=cafes, date=current_time, year=current_year)


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
        # Redirect to cafe_detail page for the updated café
        return redirect(url_for('cafe_detail', cafe_id=cafe_id))

    elif request.method == 'PATCH':
        new_price = request.form.get('new_price')
        if cafe and new_price:
            cafe.coffee_price = new_price
            db.session.commit()
            # For GET requests or unsuccessful form submissions, simply render the template with the form
    return render_template('update_price.html', cafe=cafe, form=form, date=current_time, year=current_year)


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
            # Set the delete message for successful delete
            delete_message = f'Cafe: 👌🏿 {cafe_id} 💪🏿 has been successfully deleted from the database cafe. ¡!¡'
            print(delete_message)
            return render_template('delete.html', form=form, delete_message=delete_message,
                                   date=current_time, year=current_year)
            # return jsonify({"success": f'The {cafe.name} café has been successfully deleted from the database.'}), 200
        else:
            # Set the delete message for successful delete
            error_message = f'Cafe with ID 😭 {cafe_id} 😝 not found in the database. ¡!¡'
            print(error_message)
            return render_template('delete.html', form=form, error_message=error_message,
                                   date=current_time, year=current_year)
            # return jsonify({"error": f"Cafe with ID {cafe_id} not found in the database."}), 404

    return render_template('delete.html', form=form)


@app.route('/delete-user', methods=['GET', 'POST'])
# Mark with decorator
@admin_required
def delete_user():
    form = DeleteUserForm()
    if request.method == 'POST' and form.validate_on_submit():
        user_id = form.id.data  # Get the cafe_id from the submitted form
        user = User.query.get(user_id)

        if user:
            db.session.delete(user)
            db.session.commit()
            # Set the success message for user deletion
            success_message = f'User {user_id} has been successfully deleted.'
            print(success_message)
            return render_template('delete_user.html', form=form, success_message=success_message,
                                   date=current_time, year=current_year)
        else:
            # Set the error message if user not found
            error_message = f'User with ID {user_id} not found.'
            print(error_message)
            return render_template('delete_user.html', form=form, error_message=error_message,
                                   date=current_time, year=current_year)

    return render_template('delete_user.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
