from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Όνομα Χρήστη', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Κωδικός', validators=[DataRequired()])
    confirm_password = PasswordField('Επιβεβαίωση', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Ρόλος', choices=[('user', 'Φοιτητής/Εργαζόμενος'), ('admin', 'Διαχειριστής')])
    submit = SubmitField('Εγγραφή')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Κωδικός', validators=[DataRequired()])
    submit = SubmitField('Είσοδος')

class RouteForm(FlaskForm):
    start_point = StringField('Αφετηρία', validators=[DataRequired()])
    end_point = StringField('Προορισμός', validators=[DataRequired()])
    departure_time = DateTimeLocalField('Ώρα Αναχώρησης', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    seats = IntegerField('Διαθέσιμες Θέσεις', validators=[DataRequired()])
    submit = SubmitField('Δημιουργία Διαδρομής')