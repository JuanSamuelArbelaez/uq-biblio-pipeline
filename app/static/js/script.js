let articulos = [];
let seleccionados = [];

// paginación artículos disponibles
let paginaActual = 1;
const porPagina = 10;

// paginación seleccionados
let paginaSel = 1;
const porPaginaSel = 5;

// referencias DOM
const tbody = document.querySelector("#tabla-articulos tbody");
const listaSeleccionados = document.getElementById("lista-seleccionados");
const btnAnalizar = document.getElementById("btn-analizar");
const buscarInput = document.getElementById("buscar-articulos");

// gráfico de autores
let chartAutores = null;

// botón de exportar PDF
const btnExportarPDF = document.createElement("button");
btnExportarPDF.textContent = "📄 Exportar PDF";
btnExportarPDF.className = "btn";
btnExportarPDF.disabled = true;
document.querySelector("#graficas h2").appendChild(btnExportarPDF);

/* ===============================
   🔹 Renderizado de artículos disponibles
   =============================== */
function renderArticulos() {
  tbody.innerHTML = "";
  const termino = buscarInput.value.toLowerCase();

  let filtrados = articulos.filter(a =>
    a.titulo.toLowerCase().includes(termino) ||
    a.autores.toLowerCase().includes(termino)
  );

  const totalPaginas = Math.ceil(filtrados.length / porPagina);
  if (paginaActual > totalPaginas) paginaActual = totalPaginas || 1;
  const inicio = (paginaActual - 1) * porPagina;
  const pagina = filtrados.slice(inicio, inicio + porPagina);

  pagina.forEach(a => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${a.id}</td><td>${a.titulo}</td><td>${a.autores}</td><td>${a.año}</td>`;
    if (seleccionados.some(s => s.id === a.id)) tr.classList.add("seleccionado");
    tr.addEventListener("click", () => toggleSeleccion(a));
    tbody.appendChild(tr);
  });

  document.getElementById("pagina-info").textContent = `Página ${paginaActual} de ${totalPaginas}`;
}

/* ===============================
   🔹 Renderizado de artículos seleccionados
   =============================== */
function renderSeleccionados() {
  listaSeleccionados.innerHTML = "";

  const totalPaginasSel = Math.ceil(seleccionados.length / porPaginaSel);
  if (paginaSel > totalPaginasSel) paginaSel = totalPaginasSel || 1;
  const inicioSel = (paginaSel - 1) * porPaginaSel;
  const paginaSeleccionados = seleccionados.slice(inicioSel, inicioSel + porPaginaSel);

  paginaSeleccionados.forEach(a => {
    const div = document.createElement("div");
    div.className = "articulo-item";
    div.innerHTML = `<strong>${a.titulo}</strong> (${a.año})<br><em>${a.autores}</em>`;
    const abs = document.createElement("div");
    abs.className = "articulo-abstract";
    abs.textContent = a.abstract || "Sin resumen disponible";

    div.addEventListener("click", () => {
      abs.style.display = abs.style.display === "block" ? "none" : "block";
    });

    div.appendChild(abs);
    listaSeleccionados.appendChild(div);
  });

  document.getElementById("pagina-sel-info").textContent = `Página ${paginaSel} de ${totalPaginasSel}`;
  btnAnalizar.disabled = seleccionados.length < 2;
}

/* ===============================
   🔹 Selección/deselección
   =============================== */
function toggleSeleccion(a) {
  const idx = seleccionados.findIndex(s => s.id === a.id);
  if (idx === -1) seleccionados.push(a);
  else seleccionados.splice(idx, 1);
  renderArticulos();
  renderSeleccionados();
}

/* ===============================
   🔹 Paginación artículos disponibles
   =============================== */
document.getElementById("first-page").onclick = () => { paginaActual = 1; renderArticulos(); };
document.getElementById("prev-page").onclick = () => { if (paginaActual > 1) paginaActual--; renderArticulos(); };
document.getElementById("next-page").onclick = () => {
  const max = Math.ceil(articulos.length / porPagina);
  if (paginaActual < max) paginaActual++;
  renderArticulos();
};
document.getElementById("last-page").onclick = () => {
  paginaActual = Math.ceil(articulos.length / porPagina);
  renderArticulos();
};

/* ===============================
   🔹 Paginación seleccionados
   =============================== */
document.getElementById("first-sel-page").onclick = () => { paginaSel = 1; renderSeleccionados(); };
document.getElementById("prev-sel-page").onclick = () => { if (paginaSel > 1) paginaSel--; renderSeleccionados(); };
document.getElementById("next-sel-page").onclick = () => {
  const max = Math.ceil(seleccionados.length / porPaginaSel);
  if (paginaSel < max) paginaSel++;
  renderSeleccionados();
};
document.getElementById("last-sel-page").onclick = () => {
  paginaSel = Math.ceil(seleccionados.length / porPaginaSel);
  renderSeleccionados();
};

/* ===============================
   🔹 Seleccionar/deseleccionar todos
   =============================== */
document.getElementById("btn-seleccionar-todos").onclick = () => {
  seleccionados = [...articulos];
  renderArticulos();
  renderSeleccionados();
};
document.getElementById("btn-deseleccionar-todos").onclick = () => {
  seleccionados = [];
  renderArticulos();
  renderSeleccionados();
};

/* ===============================
   🔹 Búsqueda dinámica
   =============================== */
buscarInput.addEventListener("input", () => {
  paginaActual = 1;
  renderArticulos();
});

/* ===============================
   🔹 Ejecutar análisis
   =============================== */
btnAnalizar.addEventListener("click", async () => {
  if (seleccionados.length < 2) return;

  const idsSeleccionados = seleccionados.map(a => a.id);
  const tabContent = document.getElementById("tab-content");
  tabContent.innerHTML = "<p>⏳ Ejecutando análisis...</p>";

  try {
    const resp = await fetch("/api/analisis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ids: idsSeleccionados })
    });

    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    renderTabs(data);
  } catch (e) {
    tabContent.innerHTML = `<p style="color:red;">❌ Error: ${e.message}</p>`;
  }
});

/* ===============================
   🔹 Renderizar tabs con matrices
   =============================== */
function renderTabs(resultados) {
  const tabsContainer = document.getElementById("tabs-container");
  const tabContent = document.getElementById("tab-content");
  tabsContainer.innerHTML = "";
  tabContent.innerHTML = "";

  const nombres = Object.keys(resultados);
  nombres.forEach((nombre, idx) => {
    const btn = document.createElement("button");
    btn.textContent = nombre;
    btn.className = "tab-btn";
    btn.onclick = () => mostrarTab(nombre, resultados[nombre]);
    tabsContainer.appendChild(btn);
    if (idx === 0) mostrarTab(nombre, resultados[nombre]);
  });
}

/* ===============================
   🔹 Mostrar matriz de similitud
   =============================== */
function mostrarTab(nombre, datos) {
  const tabContent = document.getElementById("tab-content");
  tabContent.innerHTML = `<h3>${nombre}</h3>`;
  const { ids, matrix } = datos;

  const container = document.createElement("div");
  container.className = "scrollable-matrix";

  const table = document.createElement("table");
  table.className = "matriz";
  const thead = document.createElement("thead");

  let header = "<tr><th></th>";
  ids.forEach(id => (header += `<th>${id}</th>`));
  header += "</tr>";
  thead.innerHTML = header;
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  ids.forEach((id, i) => {
    let row = `<tr><th>${id}</th>`;
    matrix[i].forEach(v => {
      const val = typeof v === "number" ? v.toFixed(3) : v;
      row += `<td>${val}</td>`;
    });
    row += "</tr>";
    tbody.innerHTML += row;
  });
  table.appendChild(tbody);

  container.appendChild(table);
  tabContent.appendChild(container);
}

/* ===============================
   🔹 Cargar top autores
   =============================== */
async function cargarTopAutores() {
  try {
    const resp = await fetch("/api/top_autores");
    let autores = await resp.json();

    autores.sort((a, b) => (b.Apariciones || 0) - (a.Apariciones || 0));

    const ctx = document.getElementById("graficoTopAutores").getContext("2d");
    const labels = autores.map(a => a.Autor);
    const valores = autores.map(a => a.Apariciones);

    if (chartAutores) chartAutores.destroy();

    chartAutores = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Apariciones",
          data: valores,
          borderWidth: 1
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        plugins: {
          legend: { display: false },
          title: { display: true, text: "Top 15 Autores por Apariciones" }
        },
        scales: { x: { beginAtZero: true } }
      }
    });

    checkGraficasCompletas();
  } catch (e) {
    console.error("Error al cargar top autores:", e);
  }
}

/* ===============================
   🔹 Mostrar imágenes del análisis
   =============================== */
async function cargarGraficas() {
  try {
    const resp = await fetch("/api/graficas");
    const data = await resp.json();

    const secciones = ["keywords", "location", "timeline", "wordcloud", "followup"];
    secciones.forEach(sec => {
      const cont = document.getElementById(`contenido-${sec}`);
      cont.innerHTML = data[sec]?.map(url => `<img src="${url}" class="img-grafica">`).join("") || "";
    });

    checkGraficasCompletas();
  } catch (e) {
    console.error("Error al cargar gráficas:", e);
  }
}

/* ===============================
   🔹 Habilitar botón PDF cuando todas las gráficas estén listas
   =============================== */
function checkGraficasCompletas() {
  const imgs = document.querySelectorAll("#contenidos-graficas img");
  if (chartAutores && imgs.length >= 5) btnExportarPDF.disabled = false;
}

/* ===============================
   🔹 Exportar todas las gráficas a PDF
   =============================== */
async function generarPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });

  let y = 20;
  let graficosEnPagina = 0;

  const addNewPage = () => {
    doc.addPage();
    y = 20;
    graficosEnPagina = 0;
  };

  // Portada
  doc.setFontSize(20);
  doc.text("Informe de Análisis de Producción Científica", 105, y, { align: "center" });
  y += 15;
  doc.setFontSize(12);
  doc.text("Este informe resume visualmente la producción científica a partir de las gráficas generadas en la app.", 15, y, { maxWidth: 180 });
  y += 20;
  doc.text(`Fecha de generación: ${new Date().toLocaleString("es-ES")}`, 15, y);
  y += 20;

  const agregarGrafica = (titulo, imgSrc) => {
    if (graficosEnPagina >= 2) addNewPage();
    doc.setFontSize(14);
    doc.text(titulo, 15, y);
    y += 5;
    doc.addImage(imgSrc, "PNG", 15, y, 180, 80);
    y += 90;
    graficosEnPagina++;
  };

  // Top autores
  const imgAutores = chartAutores.toBase64Image();
  agregarGrafica("Top 15 Autores por Apariciones", imgAutores);

  // Otras secciones
  const secciones = [
    { id: "contenido-location", titulo: "Mapa de calor: Distribución geográfica" },
    { id: "contenido-wordcloud", titulo: "Nube de palabras (Abstracts y Keywords)" },
    { id: "contenido-timeline", titulo: "Tendencias de publicaciones por año y revista" },
    { id: "contenido-keywords", titulo: "Coocurrencia de Keywords" },
    { id: "contenido-followup", titulo: "Red de citas / Coocurrencia" }
  ];

  for (const s of secciones) {
    const cont = document.getElementById(s.id);
    const imgs = cont.querySelectorAll("img");
    if (imgs.length > 0) {
      for (const img of imgs) {
        agregarGrafica(s.titulo, img.src);
      }
    }
  }

  doc.save("informe_graficas.pdf");
}

btnExportarPDF.addEventListener("click", generarPDF);

/* ===============================
   🔹 Cambiar entre tabs (Autores / Keywords / ETC)
   =============================== */
document.querySelectorAll("#tabs-graficas .tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#tabs-graficas .tab-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    document.querySelectorAll("#contenidos-graficas .contenido-tab").forEach(div => div.style.display = "none");
    const target = btn.id.replace("tab-", "contenido-");
    document.getElementById(target).style.display = "block";
  });
});

/* ===============================
   🔹 Cargar artículos desde API
   =============================== */
async function cargarArticulos() {
  const resp = await fetch("/api/articulos");
  articulos = await resp.json();
  renderArticulos();
  renderSeleccionados();
}

/* ===============================
   🔹 Inicialización
   =============================== */
cargarTopAutores();
cargarGraficas();
cargarArticulos();
