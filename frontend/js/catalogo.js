const API_URL = "http://127.0.0.1:5000/api/objetos";

const lista = document.getElementById("lista-objetos");
const contador = document.getElementById("contador");

const campos = {
  q: document.getElementById("f-q"),
  tipo: document.getElementById("f-tipo"),
  categoria: document.getElementById("f-categoria"),
  lugar: document.getElementById("f-lugar"),
  estado: document.getElementById("f-estado"),
  fecha_desde: document.getElementById("f-desde"),
  fecha_hasta: document.getElementById("f-hasta"),
};

const COLOR_ESTADO = {
  reportado: "danger",
  encontrado: "success",
  reclamado: "warning",
  entregado: "secondary",
};

const COLOR_TIPO = {
  extraviado: "dark",
  encontrado: "primary",
};

function escapar(texto) {
  const d = document.createElement("div");
  d.textContent = texto ?? "";
  return d.innerHTML;
}

function crearCard(o) {
  const colorEstado = COLOR_ESTADO[o.estado] || "primary";
  const colorTipo = COLOR_TIPO[o.tipo_reporte] || "info";

  return `
    <div class="col-12 col-sm-6 col-lg-4">
      <div class="card h-100 shadow-sm">
        <div class="card-body">
          <div class="mb-2">
            <span class="badge text-bg-${colorTipo}">${escapar(o.tipo_reporte)}</span>
            <span class="badge text-bg-${colorEstado}">${escapar(o.estado)}</span>
          </div>
          <h5 class="card-title">${escapar(o.titulo)}</h5>
          <p class="card-text">${escapar(o.descripcion)}</p>
        </div>
        <ul class="list-group list-group-flush">
          <li class="list-group-item"><strong>Categoría:</strong> ${escapar(o.categoria)}</li>
          <li class="list-group-item"><strong>Lugar:</strong> ${escapar(o.lugar)}</li>
          <li class="list-group-item"><strong>Fecha:</strong> ${escapar(o.fecha)}</li>
        </ul>
        <div class="card-footer text-muted small">Reportado por ${escapar(o.reportado_por)}</div>
      </div>
    </div>`;
}

async function cargarObjetos() {
  const params = new URLSearchParams();
  for (const [clave, input] of Object.entries(campos)) {
    if (input.value) params.append(clave, input.value);
  }

  try {
    const resp = await fetch(`${API_URL}?${params.toString()}`);
    if (!resp.ok) throw new Error("Error " + resp.status);
    const objetos = await resp.json();

    contador.textContent = `${objetos.length} objeto(s) encontrado(s)`;
    lista.innerHTML = objetos.length
      ? objetos.map(crearCard).join("")
      : `<div class="col-12"><div class="alert alert-info">No hay objetos con esos filtros.</div></div>`;
  } catch (e) {
    lista.innerHTML = `<div class="col-12"><div class="alert alert-danger">No se pudo cargar el catálogo: ${escapar(e.message)}</div></div>`;
  }
}

async function cargarOpcionesFiltros() {
  try {
    const resp = await fetch(`${API_URL}/filtros`);
    const { categorias, lugares } = await resp.json();
    categorias.forEach(c => campos.categoria.add(new Option(c.nombre, c.id)));
    lugares.forEach(l => campos.lugar.add(new Option(l, l)));
  } catch (e) {
    console.error("No se pudieron cargar los filtros", e);
  }
}


let temporizador;
Object.values(campos).forEach(input => {
  const evento = input.tagName === "SELECT" || input.type === "date" ? "change" : "input";
  input.addEventListener(evento, () => {
    clearTimeout(temporizador);
    temporizador = setTimeout(cargarObjetos, 300); // espera 300 ms al escribir
  });
});

document.getElementById("btn-limpiar").addEventListener("click", () => {
  document.getElementById("form-filtros").reset();
  cargarObjetos();
});

cargarOpcionesFiltros();
cargarObjetos();