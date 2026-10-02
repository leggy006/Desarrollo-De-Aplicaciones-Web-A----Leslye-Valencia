from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp


class UsuarioForm(FlaskForm):
    """Formulario de registro de usuarios."""

    usuario = StringField(
        "Usuario",
        validators=[
            DataRequired(message="El usuario es obligatorio."),
            Length(min=3, max=50, message="El usuario debe tener entre 3 y 50 caracteres."),
            Regexp(r"^[A-Za-z0-9_.]+$", message="Solo letras, números, punto y guion bajo."),
        ]
    )
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=6, message="La contraseña debe tener mínimo 6 caracteres."),
        ]
    )
    confirmar = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(message="Confirme la contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ]
    )
    submit = SubmitField("Registrarme")
