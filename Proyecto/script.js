const formulario=document.getElementById("formularioSolicitud");

const nombre=document.getElementById("nombre");
const descripcion=document.getElementById("descripcion");
const tipo=document.getElementById("tipo");

const errorNombre=document.getElementById("errorNombre");
const errorDescripcion=document.getElementById("errorDescripcion");
const errorTipo=document.getElementById("errorTipo");

const mensaje=document.getElementById("mensaje");
const lista=document.getElementById("listaSolicitudes");
const contador=document.getElementById("contador");

let total=0;


function mostrarError(campo,mensajeError,contenedor){

campo.classList.remove("is-valid");
campo.classList.add("is-invalid");

contenedor.innerHTML=`
<div class="text-danger">
${mensajeError}
</div>
`;

return false;

}


function mostrarExito(campo,contenedor){

campo.classList.remove("is-invalid");
campo.classList.add("is-valid");

contenedor.innerHTML="";

return true;

}


function validarNombre(){

if(nombre.value.trim().length<3){

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

if(descripcion.value.trim().length<10){

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

if(tipo.value===""){

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

Corrija los errores del formulario

</div>

`;

return;

}


mensaje.innerHTML=`

<div class="alert alert-success">

Solicitud agregada correctamente

</div>

`;


const tarjeta=document.createElement(
"div"
);


tarjeta.className=
"card p-3 mt-3";


tarjeta.innerHTML=`

<h5>

${nombre.value}

</h5>

<p>

${descripcion.value}

</p>

<span class="badge bg-primary">

${tipo.value}

</span>

<br><br>

<button class="btn btn-danger eliminar">

Eliminar

</button>

`;

lista.appendChild(
tarjeta
);


total++;

contador.textContent=total;


const botonEliminar=
tarjeta.querySelector(
".eliminar"
);


botonEliminar.addEventListener(

"click",

function(){

tarjeta.remove();

total--;

contador.textContent=total;

}

);


formulario.reset();

nombre.classList.remove("is-valid");
descripcion.classList.remove("is-valid");
tipo.classList.remove("is-valid");

}

);