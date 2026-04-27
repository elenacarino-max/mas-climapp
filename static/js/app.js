document.getElementById("form-registro").addEventListener("submit", function(e){
    e.preventDefault();

    const mensajeDiv = document.getElementById("mensaje");

    // 1. Captura de datos desde el DOM.
    const datos = {
        estacion_id: document.getElementById("estacion_id").value,
        fecha:       document.getElementById("fecha").value,
        temperatura: parseFloat(document.getElementById("temperatura").value),
        humedad:     parseFloat(document.getElementById("humedad").value),
        viento:      parseFloat(document.getElementById("viento").value),
        lluvia:      parseFloat(document.getElementById("lluvia").value),
    };

    // 2. Validación lógica rápida (Sincronizada con validators.py).
    if (isNaN(datos.humedad) || datos.humedad < 0 || datos.humedad > 100){
        mensajeDiv.innerText = "❌ La humedad debe estar entre 0% y 100%";
        mensajeDiv.style.color = "#ef4444";
        return;
    }

    // 3. Simulación de éxito tras validación local.
    mensajeDiv.innerText = "✔ Registro completado con éxito"
    mensajeDiv.style.color = "#22c55e"

    // El objeto ya contiene tipos númericos gracias al parseFloat.
    console.log("Objeto listo para el modelo:", datos)
})