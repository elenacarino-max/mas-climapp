function actualizarIconoVisual(data) {
    const container = document.getElementById("weather-icon-container");
    const sun = document.getElementById("sun-icon");

    if (!container || !sun) return;

    container.querySelectorAll(".cloud, .rain-drops").forEach((el) => el.remove());
    sun.className = "sun";

    if (data.es_noche) {
        sun.classList.add("is-night");
    }

    const temp = Number(data.temperatura);
    if (!Number.isNaN(temp)) {
        if (temp <= 12) {
            sun.classList.add("temp-cold");
        } else if (temp >= 28) {
            sun.classList.add("temp-hot");
        }
    }

    const lluvia = Number(data.lluvia || 0);
    const humedad = Number(data.humedad || 0);

    if (lluvia > 0) {
        crearNube(container, true);
    } else if (humedad > 75) {
        crearNube(container, false);
    }
}

function crearNube(parent, conLluvia) {
    const cloud = document.createElement("div");
    cloud.className = "cloud";

    if (conLluvia) {
        const drops = document.createElement("div");
        drops.className = "rain-drops";

        for (let i = 0; i < 3; i += 1) {
            const drop = document.createElement("div");
            drop.className = "drop";
            drop.style.left = `${20 + i * 25}px`;
            drop.style.animationDelay = `${i * 0.2}s`;
            drops.appendChild(drop);
        }

        cloud.appendChild(drops);
    }

    parent.appendChild(cloud);
}

function formatearNumero(valor, decimales = 0) {
    const numero = Number(valor);

    if (Number.isNaN(numero)) {
        return "--";
    }

    return numero.toLocaleString("es-ES", {
        maximumFractionDigits: decimales,
        minimumFractionDigits: 0,
    });
}

function pintarClima(data) {
    const temperature = document.getElementById("temperature");
    const humidity = document.getElementById("humidity");
    const wind = document.getElementById("wind");
    const rain = document.getElementById("rain");
    const source = document.getElementById("source");
    const stationName = document.getElementById("stationName");
    const cityName = document.getElementById("cityName");
    const mainTitle = document.getElementById("mainTitle");
    const updatedAt = document.getElementById("updatedAt");
    const statusDot = document.getElementById("statusDot");

    temperature.textContent = `${formatearNumero(data.temperatura)}°`;
    humidity.textContent = `${formatearNumero(data.humedad)}%`;
    wind.textContent = `${formatearNumero(data.viento, 1)} km/h`;
    rain.textContent = `${formatearNumero(data.lluvia, 1)} mm`;
    source.textContent = (data.fuente || "AEMET").toUpperCase();
    stationName.textContent = data.estacion || "Estacion no disponible";
    cityName.textContent = data.ciudad || data.municipio || "Ubicacion detectada";
    mainTitle.textContent = `${cityName.textContent} · tiempo real`;

    const horaActual = new Date().toLocaleTimeString("es-ES", {
        hour: "2-digit",
        minute: "2-digit",
    });

    updatedAt.textContent = `Ultima actualizacion: ${horaActual}`;
    actualizarIconoVisual(data);

    statusDot.style.background = "#16a34a";
    statusDot.style.boxShadow = "0 0 0 5px rgba(22, 163, 74, 0.12)";
}

async function consultarClima(url) {
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "No se pudo consultar AEMET");
    }

    pintarClima(data);
}

async function actualizarClima() {
    const updatedAt = document.getElementById("updatedAt");
    const statusDot = document.getElementById("statusDot");

    if (!navigator.geolocation) {
        updatedAt.textContent = "GPS no soportado";
        statusDot.style.background = "#dc2626";
        return;
    }

    updatedAt.textContent = "Localizando...";

    navigator.geolocation.getCurrentPosition(async (position) => {
        const { latitude, longitude } = position.coords;

        try {
            await consultarClima(`/api/clima?lat=${latitude}&lon=${longitude}`);
        } catch (error) {
            console.error(error);
            updatedAt.textContent = "Error de conexion con AEMET";
            statusDot.style.background = "#dc2626";
            statusDot.style.boxShadow = "0 0 0 5px rgba(220, 38, 38, 0.12)";
        }
    }, () => {
        updatedAt.textContent = "Permiso de ubicacion denegado";
        statusDot.style.background = "#dc2626";
        statusDot.style.boxShadow = "0 0 0 5px rgba(220, 38, 38, 0.12)";
    });
}

function pintarEstado(servicio, estado, texto) {
    const dot = document.getElementById(`${servicio}StatusDot`);
    const label = document.getElementById(`${servicio}StatusText`);

    if (!dot || !label) return;

    dot.classList.remove("pending", "error");

    if (estado === "ok" || estado === "configured") {
        dot.style.background = "#16a34a";
        dot.style.boxShadow = "0 0 0 5px rgba(22, 163, 74, 0.12)";
    } else {
        dot.classList.add("error");
        dot.style.background = "";
        dot.style.boxShadow = "";
    }

    label.textContent = texto;
}

async function actualizarEstadoServicios() {
    try {
        const response = await fetch("/api/status");
        const data = await response.json();

        pintarEstado("flask", data.flask?.status, "Disponible en puerto 5000");

        const fastapiOk = data.fastapi?.status === "ok";
        pintarEstado(
            "fastapi",
            data.fastapi?.status,
            fastapiOk ? "Swagger activo en puerto 8000" : "Pendiente: arranca Uvicorn"
        );

        pintarEstado(
            "db",
            data.database?.status,
            data.database?.status === "ok" ? "Conexion SQL disponible" : "Revisar base de datos"
        );
    } catch (error) {
        console.error(error);
        pintarEstado("flask", "error", "No se pudo leer /api/status");
        pintarEstado("fastapi", "error", "Sin comprobar");
        pintarEstado("db", "error", "Sin comprobar");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    actualizarClima();
    actualizarEstadoServicios();

    const refreshBtn = document.getElementById("refreshBtn");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", actualizarClima);
    }

    const statusRefreshBtn = document.getElementById("statusRefreshBtn");
    if (statusRefreshBtn) {
        statusRefreshBtn.addEventListener("click", actualizarEstadoServicios);
    }

});
