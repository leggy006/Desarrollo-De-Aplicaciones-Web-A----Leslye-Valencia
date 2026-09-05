from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class SolicitudForm(FlaskForm):
    """Formulario para registrar una nueva solicitud de trabajo artístico."""

    nombre = StringField(
        "Nombre cliente",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=3, message="El nombre debe tener mínimo 3 caracteres.")
        ]
    )

    descripcion = TextAreaField(
        "Descripción",
        validators=[
            DataRequired(message="La descripción es obligatoria."),
            Length(min=10, message="Debe escribir mínimo 10 caracteres.")
        ]
    )

    tipo = SelectField(
        "Tipo",
        choices=[
            ("", "Seleccione"),
            ("Retrato personalizado", "Retrato personalizado"),
            ("Caricatura a lápiz", "Caricatura a lápiz"),
            ("Pintura personalizada", "Pintura personalizada"),
        ],
        validators=[DataRequired(message="Seleccione una categoría.")]
    )

    submit = SubmitField("Agregar solicitud")
