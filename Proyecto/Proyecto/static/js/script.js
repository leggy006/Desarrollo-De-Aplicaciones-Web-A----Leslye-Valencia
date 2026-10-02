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

    const cliente = document.getElementById("cliente");
    const descripcion = document.getElementById("descripcion");
    const tipo = document.getElementById("tipo");

    const errorCliente = document.getElementById("errorCliente");
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

    function validarCliente() {
        if (cliente.value === "") {
            return mostrarError(cliente, "Seleccione un cliente", errorCliente);
        }
        return mostrarExito(cliente, errorCliente);
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

    cliente.addEventListener("change", validarCliente);
    descripcion.addEventListener("input", validarDescripcion);
    descripcion.addEventListener("blur", validarDescripcion);
    tipo.addEventListener("change", validarTipo);

    // La validación real y definitiva ocurre en el servidor con Flask-WTF.
    // Aquí solo damos feedback visual inmediato; si todo luce válido,
    // dejamos que el formulario se envíe de forma normal (POST a Flask),
    // que es quien hace el INSERT en PostgreSQL y recarga la página con el SELECT actualizado.
    formulario.addEventListener("submit", function (e) {
        const clienteValido = validarCliente();
        const descripcionValida = validarDescripcion();
        const tipoValido = validarTipo();

        if (!clienteValido || !descripcionValida || !tipoValido) {
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


// ---------------------------------------------------------------
// Confirmación antes de eliminar: el modal recibe la URL y el nombre
// del registro seleccionado desde el botón que lo abrió.
// ---------------------------------------------------------------
const modalEliminar = document.getElementById("modalEliminar");

if (modalEliminar) {
    modalEliminar.addEventListener("show.bs.modal", function (evento) {
        const boton = evento.relatedTarget;
        document.getElementById("formEliminar").action = boton.dataset.url;
        document.getElementById("eliminarNombre").textContent = boton.dataset.nombre;
    });
}


// ---------------------------------------------------------------
// Botones "Copiar": copian el texto del elemento indicado en data-copiar.
// ---------------------------------------------------------------
document.addEventListener("click", function (evento) {
    const boton = evento.target.closest("[data-copiar]");
    if (!boton) {
        return;
    }
    const origen = document.querySelector(boton.dataset.copiar);
    if (origen && navigator.clipboard) {
        navigator.clipboard.writeText(origen.textContent.trim()).then(function () {
            const original = boton.innerHTML;
            boton.innerHTML = '<i class="bi bi-check2"></i> Copiado';
            setTimeout(function () { boton.innerHTML = original; }, 1500);
        });
    }
});


// ---------------------------------------------------------------
// Pagos: muestra el valor a transferir según el servicio elegido.
// Los precios llegan desde PostgreSQL en data-precios.
// ---------------------------------------------------------------
const selectServicio = document.getElementById("servicio");
const montoPagar = document.getElementById("montoPagar");

if (selectServicio && montoPagar) {
    const precios = JSON.parse(selectServicio.dataset.precios || "{}");

    function mostrarMonto() {
        const precio = precios[selectServicio.value];
        montoPagar.textContent = precio ? "$" + precio : "$0.00";
    }

    selectServicio.addEventListener("change", mostrarMonto);
    mostrarMonto();
}
