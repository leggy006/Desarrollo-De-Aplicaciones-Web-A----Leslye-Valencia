from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp


class ClienteForm(FlaskForm):
    """Formulario para registrar o modificar un cliente."""

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=3, max=100, message="El nombre debe tener entre 3 y 100 caracteres.")
        ]
    )

    telefono = StringField(
        "Teléfono",
        validators=[
            Optional(),
            Regexp(r"^[0-9+ ]{7,20}$", message="Use solo números (7 a 20 dígitos).")
        ]
    )

    correo = StringField(
        "Correo",
        validators=[
            Optional(),
            Email(message="Ingrese un correo válido."),
            Length(max=100)
        ]
    )

    submit = SubmitField("Agregar cliente")
