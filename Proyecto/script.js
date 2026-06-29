const formulario=document.getElementById(
"formularioSolicitud"
);

const nombre=document.getElementById(
"nombre"
);

const descripcion=document.getElementById(
"descripcion"
);

const tipo=document.getElementById(
"tipo"
);

const mensaje=document.getElementById(
"mensaje"
);

const lista=document.getElementById(
"listaSolicitudes"
);

const contador=document.getElementById(
"contador"
);

let total=0;


formulario.addEventListener(

"submit",

function(e){

e.preventDefault();


if(

nombre.value===""

||

descripcion.value===""

||

tipo.value===""

){

mensaje.innerHTML=`

<div class="alert alert-danger">

Todos los campos son obligatorios

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

}

);