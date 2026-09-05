// ---------------------------------------------------------------
// Galería de Servicios: al hacer clic en una miniatura, se muestra
// ampliada dentro del modal reutilizable #modalGaleria.
// ---------------------------------------------------------------
document.addEventListener("click", function (evento) {
    const miniatura = evento.target.closest(".galeria-img");
    if (!miniatura) {
        return;
    }
    const imagenModal = document.getElementById("modalGaleriaImg");
    if (imagenModal) {
        imagenModal.src = miniatura.src;
        imagenModal.alt = miniatura.alt;
    }
});

const formulario = document.getElementById("formularioSolicitud");

// Este script se carga en todas las páginas (viene desde base.html),
// pero el formulario de solicitudes solo existe en /solicitudes.
// Por eso todo el código se ejecuta únicamente si el formulario existe.
if (formulario) {

    const nombre = document.getElementById("nombre");
    const descripcion = document.getElementById("descripcion");
    const tipo = document.getElementById("tipo");

    const errorNombre = document.getElementById("errorNombre");
    const errorDescripcion = document.getElementById("errorDescripcion");
    const errorTipo = document.getElementById("errorTipo");

    const mensaje = document.getElementById("mensaje");
    const spinner = document.getElementById("spinnerCarga");

    function mostrarError(campo, mensajeError, contenedor) {
        campo.classList.remove("is-valid");
        campo.classList.add("is-invalid");
        contenedor.innerHTML = `<div class="text-danger">${mensajeError}</div>`;
        return false;
    }

    function mostrarExito(campo, contenedor) {
        campo.classList.remove("is-invalid");
        campo.classList.add("is-valid");
        contenedor.innerHTML = "";
        return true;
    }

    function validarNombre() {
        if (nombre.value.trim().length < 3) {
            return mostrarError(nombre, "El nombre debe tener mínimo 3 caracteres", errorNombre);
        }
        return mostrarExito(nombre, errorNombre);
    }

    function validarDescripcion() {
        if (descripcion.value.trim().length < 10) {
            return mostrarError(descripcion, "Debe escribir mínimo 10 caracteres", errorDescripcion);
        }
        return mostrarExito(descripcion, errorDescripcion);
    }

    function validarTipo() {
        if (tipo.value === "") {
            return mostrarError(tipo, "Seleccione una categoría", errorTipo);
        }
        return mostrarExito(tipo, errorTipo);
    }

    nombre.addEventListener("input", validarNombre);
    nombre.addEventListener("blur", validarNombre);
    descripcion.addEventListener("input", validarDescripcion);
    descripcion.addEventListener("blur", validarDescripcion);
    tipo.addEventListener("change", validarTipo);

    // La validación real y definitiva ocurre en el servidor con Flask-WTF.
    // Aquí solo damos feedback visual inmediato; si todo luce válido,
    // dejamos que el formulario se envíe de forma normal (POST a Flask),
    // que es quien hace el INSERT en SQLite y recarga la página con el SELECT actualizado.
    formulario.addEventListener("submit", function (e) {
        const nombreValido = validarNombre();
        const descripcionValida = validarDescripcion();
        const tipoValido = validarTipo();

        if (!nombreValido || !descripcionValida || !tipoValido) {
            e.preventDefault();
            mensaje.innerHTML = `<div class="alert alert-danger">Corrija los errores del formulario.</div>`;
            return;
        }

        mensaje.innerHTML = "";
        if (spinner) {
            spinner.style.display = "block";
        }
        // No se llama a e.preventDefault(): el formulario continúa su envío normal hacia Flask.
    });
}
