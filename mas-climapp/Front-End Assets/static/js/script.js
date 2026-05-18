// =====================================================================
// MADRID WEATHER DASHBOARD - MASTER SCRIPT (CLEANED)
// =====================================================================

document.addEventListener("DOMContentLoaded", () => {
  // ---------------------------------------------------------
  // 1. DASHBOARD PAGE LOGIC (Map & Stats)
  // ---------------------------------------------------------
  const mapElement = document.getElementById("map");

  if (mapElement) {
    var map = L.map("map").setView([40.4167, -3.7033], 10);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    function createPopupContent(name, id, temp, hum, wind) {
      return `
        <div class="hover-card">
          <div class="card-header">${name}</div>
          <div class="card-body">
            <div class="stat-row"><i class="fas fa-thermometer-half temp-icon"></i> <span>${temp ? temp + "°C" : "--"}</span></div>
            <div class="stat-row"><i class="fas fa-tint hum-icon"></i> <span>${hum ? hum + "%" : "--"}</span></div>
            <div class="stat-row"><i class="fas fa-wind wind-icon"></i> <span>${wind ? wind + " km/h" : "--"}</span></div>
          </div>
          <div class="card-footer">ID: ${id} | Datos en Vivo</div>
        </div>
      `;
    }

    // 1. Fetch real DB data -> 2. Fetch coordinates -> 3. Plot Map
    fetch("/api/mapa_datos")
      .then((response) => response.json())
      .then((dbData) => {
        fetch("/static/weather_history.json")
          .then((res) => res.json())
          .then((geoData) => {
            dbData.forEach((dbStation) => {
              const coords = geoData.find(
                (g) => g.id.toString() === dbStation.id_estacion.toString(),
              );
              if (coords) {
                L.marker([coords.lat, coords.lon])
                  .addTo(map)
                  .bindPopup(
                    createPopupContent(
                      dbStation.municipio,
                      dbStation.id_estacion,
                      dbStation.temperatura,
                      dbStation.humedad,
                      dbStation.viento,
                    ),
                  );
              }
            });
          });
      })
      .catch((err) => console.error("Error loading map data:", err));

    setTimeout(() => {
      map.invalidateSize();
    }, 500);
  }

  // ---------------------------------------------------------
  // 2. FORM LIBRARIES & INPUT LISTENERS
  // ---------------------------------------------------------
  if (document.getElementById("time_picker")) {
    flatpickr("#time_picker", {
      enableTime: true,
      noCalendar: true,
      dateFormat: "H:i",
      time_24hr: true,
    });
  }

  const csvInput = document.getElementById("real-csv-input");
  if (csvInput) {
    csvInput.addEventListener("change", function (e) {
      if (e.target.files.length > 0) {
        document.getElementById("file-name-display").innerText =
          "📁 " + e.target.files[0].name;
      }
    });
  }

  const jsonInput = document.getElementById("real-json-input");
  if (jsonInput) {
    jsonInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        document.getElementById("json-file-name-display").innerText =
          "{ } " + e.target.files[0].name;
      }
    });
  }

  const btnSaveProfile = document.querySelector(".btn-save");
  if (btnSaveProfile) {
    btnSaveProfile.addEventListener("click", function () {
      alert("¡Perfil actualizado correctamente!");
    });
  }
});

// =====================================================================
// 3. GLOBAL FUNCTIONS (Modals & Tabs)
// =====================================================================

function toggleForm() {
  const form = document.getElementById("registro-form-container");
  const tableView = document.querySelector(".data-view-container");
  if (form && tableView) {
    if (form.style.display === "none") {
      form.style.display = "block";
      tableView.style.display = "none";
    } else {
      form.style.display = "none";
      tableView.style.display = "block";
    }
  }
}

// --- CSV MODAL & UPLOAD ---
function openCsvModal() {
  document.getElementById("csv-modal").style.display = "flex";
}
function closeCsvModal() {
  document.getElementById("csv-modal").style.display = "none";
}
function processCsvUpload() {
  const fileInput = document.getElementById("real-csv-input");
  if (fileInput.files.length === 0)
    return alert("Selecciona un archivo CSV primero.");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  fetch("/upload_csv", { method: "POST", body: formData })
    .then((response) => response.json())
    .then((data) => {
      alert("Éxito: " + data.message);
      closeCsvModal();
      window.location.href = "/";
    })
    .catch((error) => alert("Error al subir el archivo CSV al servidor."));
}

// --- JSON MODAL & UPLOAD ---
function openJsonModal() {
  document.getElementById("json-modal").style.display = "flex";
}
function closeJsonModal() {
  document.getElementById("json-modal").style.display = "none";
}
function processJsonUpload() {
  const fileInput = document.getElementById("real-json-input");
  if (fileInput.files.length === 0)
    return alert("Selecciona un archivo JSON primero.");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  fetch("/upload_json", { method: "POST", body: formData })
    .then((response) => response.json())
    .then((data) => {
      alert("Éxito: " + data.message);
      closeJsonModal();
      window.location.href = "/";
    })
    .catch((error) => alert("Error al subir el archivo JSON al servidor."));
}

// --- SETTINGS TABS & STAFF MODALS ---
function openTab(evt, tabName) {
  document
    .querySelectorAll(".tab-content")
    .forEach((tab) => (tab.style.display = "none"));
  document
    .querySelectorAll(".tab-btn")
    .forEach((btn) => btn.classList.remove("active"));
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.classList.add("active");
}

function openStaffModal() {
  document.getElementById("staff-modal").style.display = "flex";
}
function closeStaffModal() {
  document.getElementById("staff-modal").style.display = "none";
}
