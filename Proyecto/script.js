const formulario = document.getElementById("formularioSolicitud");

const nombre = document.getElementById("nombre");
const descripcion = document.getElementById("descripcion");
const tipo = document.getElementById("tipo");

const errorNombre = document.getElementById("errorNombre");
const errorDescripcion = document.getElementById("errorDescripcion");
const errorTipo = document.getElementById("errorTipo");

const mensaje = document.getElementById("mensaje");

const spinner = document.getElementById("spinnerCarga");

const lista = document.getElementById("listaSolicitudes");
const contador = document.getElementById("contador");
const sinDatos = document.getElementById("sinDatos");

let solicitudes = [];



function mostrarError(campo, mensajeError, contenedor){

    campo.classList.remove("is-valid");
    campo.classList.add("is-invalid");

    contenedor.innerHTML = `
    <div class="text-danger">
        ${mensajeError}
    </div>
    `;

    return false;

}



function mostrarExito(campo, contenedor){

    campo.classList.remove("is-invalid");
    campo.classList.add("is-valid");

    contenedor.innerHTML = "";

    return true;

}



function validarNombre(){

    if(nombre.value.trim().length < 3){

        return mostrarError(
            nombre,
            "El nombre debe tener mínimo 3 caracteres",
            errorNombre
        );

    }

    return mostrarExito(
        nombre,
        errorNombre
    );

}



function validarDescripcion(){

    if(descripcion.value.trim().length < 10){

        return mostrarError(
            descripcion,
            "Debe escribir mínimo 10 caracteres",
            errorDescripcion
        );

    }

    return mostrarExito(
        descripcion,
        errorDescripcion
    );

}



function validarTipo(){

    if(tipo.value === ""){

        return mostrarError(
            tipo,
            "Seleccione una categoría",
            errorTipo
        );

    }

    return mostrarExito(
        tipo,
        errorTipo
    );

}



function renderizarSolicitudes(){

    lista.innerHTML = "";

    if(solicitudes.length === 0){

        lista.innerHTML = `
        <p id="sinDatos" class="text-center text-muted">
            No existen solicitudes registradas.
        </p>
        `;

        contador.textContent = 0;

        return;

    }

    solicitudes.forEach(function(solicitud, indice){

        lista.innerHTML += `

        <div class="card p-3 mt-3">

            <h5>

                ${solicitud.nombre}

            </h5>

            <p>

                ${solicitud.descripcion}

            </p>

            <span class="badge bg-primary">

                ${solicitud.tipo}

            </span>

            <br><br>

            <button
                class="btn btn-danger"
                onclick="eliminarSolicitud(${indice})">

                Eliminar

            </button>

        </div>

        `;

    });

    contador.textContent = solicitudes.length;

}



function eliminarSolicitud(indice){

    solicitudes.splice(indice,1);

    renderizarSolicitudes();

}



nombre.addEventListener(
    "input",
    validarNombre
);

nombre.addEventListener(
    "blur",
    validarNombre
);

descripcion.addEventListener(
    "input",
    validarDescripcion
);

descripcion.addEventListener(
    "blur",
    validarDescripcion
);

tipo.addEventListener(
    "change",
    validarTipo
);
formulario.addEventListener(

"submit",

function(e){

e.preventDefault();

let nombreValido=validarNombre();
let descripcionValida=validarDescripcion();
let tipoValido=validarTipo();


if(

!nombreValido ||
!descripcionValida ||
!tipoValido

){

mensaje.innerHTML=`

<div class="alert alert-danger">

Corrija los errores del formulario.

</div>

`;

return;

}


spinner.style.display = "block";

mensaje.innerHTML = "";

setTimeout(function(){

spinner.style.display = "none";

const nuevaSolicitud={

nombre:nombre.value.trim(),

descripcion:descripcion.value.trim(),

tipo:tipo.value

};


solicitudes.push(
nuevaSolicitud
);


renderizarSolicitudes();


mensaje.innerHTML=`

<div class="alert alert-success">

Solicitud agregada correctamente.

</div>

`;

},1500);


formulario.reset();

nombre.classList.remove("is-valid");

descripcion.classList.remove("is-valid");

tipo.classList.remove("is-valid");

errorNombre.innerHTML="";
errorDescripcion.innerHTML="";
errorTipo.innerHTML="";

nombre.focus();

}

);


renderizarSolicitudes();