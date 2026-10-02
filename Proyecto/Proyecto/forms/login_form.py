from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    usuario = StringField("Usuario", validators=[DataRequired(message="Ingrese su usuario.")])
    password = PasswordField("Contraseña", validators=[DataRequired(message="Ingrese su contraseña.")])
    submit = SubmitField("Iniciar sesión")
