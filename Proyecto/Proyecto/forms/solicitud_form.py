from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class SolicitudForm(FlaskForm):
    """Formulario para registrar o modificar una solicitud de trabajo artístico."""

    # Las opciones de cliente y tipo se cargan desde PostgreSQL en la ruta.
    cliente = SelectField(
        "Cliente",
        choices=[],
        validators=[DataRequired(message="Seleccione un cliente.")]
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
        choices=[],
        validators=[DataRequired(message="Seleccione una categoría.")]
    )

    submit = SubmitField("Agregar solicitud")
