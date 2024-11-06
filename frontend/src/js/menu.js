
const cloud = document.getElementById("cloud");
const barraLateral = document.querySelector(".barra-lateral");
const spans = document.querySelectorAll("span");
const palanca = document.querySelector(".switch");
const circulo = document.querySelector(".circulo");
const menu = document.querySelector(".menu");
const main = document.querySelector("main");

/* EFECTO PARA NUEVO REGISTRO */


/* EFECTO PARA NUEVO REGISTRO */

// Obtener elementos del DOM
const popup = document.getElementById('popup');
const nuevoRegistroBtn = document.getElementById('nuevoRegistroBtn');
const closeBtn = document.querySelector('.close-btn');
const formContainer = document.getElementById('form-container');
const successMessage = document.getElementById('success-message');
const errorMessage = document.getElementById('error-message');
const uploadForm = document.getElementById('upload-form');

// Mostrar el popup
nuevoRegistroBtn.addEventListener('click', () => {
    popup.style.display = 'flex';
    // Reiniciar el estado del popup y formulario
    formContainer.style.display = 'block';
    successMessage.style.display = 'none';
    errorMessage.style.display = 'none';
    uploadForm.reset(); // Reiniciar el formulario
});

// Ocultar el popup
closeBtn.addEventListener('click', () => {
    popup.style.display = 'none';
});

// Ocultar el popup al hacer clic fuera del contenido
window.addEventListener('click', (event) => {
    if (event.target === popup) {
        popup.style.display = 'none';
    }
});

// Manejar la respuesta del formulario
uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevenir el envío del formulario para manejarlo con JS

    const formData = new FormData(uploadForm);

    try {
        const response = await fetch(uploadForm.action, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            // Mostrar el mensaje de éxito
            formContainer.style.display = 'none';
            successMessage.style.display = 'block';
            errorMessage.style.display = 'none';
        } else {
            // Mostrar el mensaje de error
            formContainer.style.display = 'none';
            successMessage.style.display = 'none';
            errorMessage.style.display = 'block';
        }
    } catch (error) {
        // Mostrar el mensaje de error
        console.error('Error al cargar el archivo:', error);
        formContainer.style.display = 'none';
        successMessage.style.display = 'none';
        errorMessage.style.display = 'block';
    }
}); // Cierre del bloque

// Agregar un botón para permitir al usuario intentar cargar otro archivo
const retryButton = document.createElement('button');
retryButton.textContent = 'Intentar de nuevo';
retryButton.className = 'retry-btn';

retryButton.addEventListener('click', () => {
    formContainer.style.display = 'block';
    successMessage.style.display = 'none';
    errorMessage.style.display = 'none';
    uploadForm.reset(); // Reiniciar el formulario
});

successMessage.appendChild(retryButton);
errorMessage.appendChild(retryButton);

/* NUEVO REGISTRO */

menu.addEventListener("click", () => {
    barraLateral.classList.toggle("max-barra-lateral");
    if (barraLateral.classList.contains("max-barra-lateral")) {
        menu.children[0].style.display = "none";
        menu.children[1].style.display = "block";
    } else {
        menu.children[0].style.display = "block";
        menu.children[1].style.display = "none";
    }
    if (window.innerWidth <= 320) {
        barraLateral.classList.add("mini-barra-lateral");
        main.classList.add("min-main");
        spans.forEach((span) => {
            span.classList.add("oculto");
        });
    }
});

cloud.addEventListener("click", () => {
    barraLateral.classList.toggle("mini-barra-lateral");
    main.classList.toggle("min-main");
    spans.forEach((span) => {
        span.classList.toggle("oculto");
    });
});


/* NUEVO REGISTRO Y ERROR Y BIEN AL CARGAR */

menu.addEventListener("click",()=>{
    barraLateral.classList.toggle("max-barra-lateral");
    if(barraLateral.classList.contains("max-barra-lateral")){
        menu.children[0].style.display = "none";
        menu.children[1].style.display = "block";
    }
    else{
        menu.children[0].style.display = "block";
        menu.children[1].style.display = "none";
    }
    if(window.innerWidth<=320){
        barraLateral.classList.add("mini-barra-lateral");
        main.classList.add("min-main");
        spans.forEach((span)=>{
            span.classList.add("oculto");
        })
    }
});

cloud.addEventListener("click",()=>{
    barraLateral.classList.toggle("mini-barra-lateral");
    main.classList.toggle("min-main");
    spans.forEach((span)=>{
        span.classList.toggle("oculto");
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const nuevoRegistroBtn = document.getElementById('nuevoRegistroBtn');
    const popup = document.getElementById('popup');
    const closePopupBtn = document.querySelector('.popup .close-btn');

    // Mostrar el popup cuando se hace clic en "Nuevo Registro"
    nuevoRegistroBtn.addEventListener('click', function () {
        popup.style.display = 'flex'; // Mostrar el popup
        // Reiniciar el formulario y los mensajes de estado
        document.getElementById('form-container').style.display = 'block';
        document.getElementById('success-message').style.display = 'none';
        document.getElementById('error-message').style.display = 'none';
        document.getElementById('upload-form').reset();
    });

    // Cerrar el popup cuando se hace clic en el botón de cerrar
    closePopupBtn.addEventListener('click', function () {
        popup.style.display = 'none'; // Ocultar el popup
    });

    // Cerrar el popup si se hace clic fuera de su contenido
    window.addEventListener('click', function (event) {
        if (event.target === popup) {
            popup.style.display = 'none'; // Ocultar el popup
        }
    });
});

