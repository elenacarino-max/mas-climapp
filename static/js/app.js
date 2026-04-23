document.getElementById("form-registro").addEventListener("submit", function(e){
    e.preventDefault();

    const mensajeDiv = document.getElementById("mensaje");

    // 1. Captura de datos
    const datos = {
        estacion_id: document.getElementById("estacion_id").value,
        fecha: document.getElementById("fecha").value,
        temperatura: document.getElementById("temperatura").value,
        humedad: document.getElementById("viento").value,
        viento: document.getElementById("viento").value,
        lluvia: document.getElementById("lluvia").value
    };

    // 2. Validación lógica rápida (basada en validators.py)
    if (datos.humedad < 0 || datos.humedad > 100){
        mensajeDiv.innerText = "⚠ La humedad debe estar entre 0% y 100%";
        mensajeDiv.style.color = "#f59eb0";
        return;
    }

    // 3. Simulación de éxito
    // Aquí se llamrá al controlador manual
    mensajeDiv.innerText = "✔ Registro completado con éxito"
    mensajeDiv.style.color = "#22c55e"

    console.log("Objeto listo para el modelo:", datos)

})