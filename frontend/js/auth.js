const API_URL = "http://127.0.0.1:5000/api/auth/login";

document.getElementById("formLogin").addEventListener("submit", async function (e) {
    e.preventDefault(); // Evita que la página se recargue

    const correo = document.getElementById("correo").value;
    const password = document.getElementById("password").value;
    const alerta = document.getElementById("alerta");

    try {
        const respuesta = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ correo, password })
        });

        const datos = await respuesta.json();

        if (respuesta.ok) {
            // Guardar el Token JWT y los datos del usuario en localStorage
            localStorage.setItem("token", datos.token);
            localStorage.setItem("usuario", JSON.stringify(datos.usuario));

            alerta.className = "alert alert-success";
            alerta.textContent = `¡Bienvenido, ${datos.usuario.nombre}! Redirigiendo...`;
            alerta.classList.remove("d-none");

            // Redirigir al catálogo después de 1.5 segundos
            setTimeout(() => {
                window.location.href = "catalogo.html";
            }, 1500);
        } else {
            alerta.className = "alert alert-danger";
            alerta.textContent = datos.mensaje || "Error al iniciar sesión";
            alerta.classList.remove("d-none");
        }
    } catch (error) {
        alerta.className = "alert alert-danger";
        alerta.textContent = "No se pudo conectar con el servidor Flask.";
        alerta.classList.remove("d-none");
    }
});