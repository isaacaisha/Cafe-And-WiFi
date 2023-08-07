from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField, PasswordField
from wtforms.validators import DataRequired


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


class DeleteUserForm(FlaskForm):
    id = IntegerField('User\'s ID to Delete:', validators=[DataRequired()])
    submit = SubmitField('Delete User')
