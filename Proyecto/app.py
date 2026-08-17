from flask import Flask, render_template

app = Flask(__name__)

# Datos de ejemplo (estáticos, sin base de datos por ahora)
servicios_data = [
    {
        "titulo": "Retratos personalizados",
        "descripcion": "Retratos únicos personalizados a partir de tus fotos favoritas."
    },
    {
        "titulo": "Dibujos a lápiz",
        "descripcion": "Creaciones artísticas detalladas realizadas a mano."
    },
    {
        "titulo": "Ilustraciones digitales",
        "descripcion": "Diseños digitales personalizados para cualquier ocasión."
    }
]

solicitudes_data = [
    {
        "nombre": "María Pérez",
        "descripcion": "Retrato familiar en blanco y negro, formato A4.",
        "tipo": "Retrato personalizado"
    },
    {
        "nombre": "Juan Torres",
        "descripcion": "Dibujo a lápiz de su mascota (perro Kira).",
        "tipo": "Dibujo a lápiz"
    }
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/servicios")
def servicios():
    return render_template("servicios.html", servicios=servicios_data)


@app.route("/contacto")
def contacto():
    return render_template("contacto.html")


@app.route("/solicitudes")
def solicitudes():
    return render_template("solicitudes.html", solicitudes=solicitudes_data)


if __name__ == "__main__":
    app.run(debug=True)
