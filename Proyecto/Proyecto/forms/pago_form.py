from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class PagoForm(FlaskForm):
    """Formulario para reportar un pago por transferencia."""

    servicio = SelectField(
        "Servicio",
        choices=[],
        validators=[DataRequired(message="Seleccione el servicio.")]
    )

    codigo = StringField(
        "Código de la transferencia",
        validators=[
            DataRequired(message="Ingrese el código de la transferencia."),
            Length(min=4, max=50, message="El código debe tener entre 4 y 50 caracteres."),
            Regexp(r"^[A-Za-z0-9\-]+$", message="Use solo letras, números y guiones.")
        ]
    )

    comprobante = FileField(
        "Foto del comprobante",
        validators=[
            FileRequired(message="Suba la foto del comprobante."),
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Solo imágenes JPG, PNG o WEBP.")
        ]
    )

    submit = SubmitField("Enviar pago")
