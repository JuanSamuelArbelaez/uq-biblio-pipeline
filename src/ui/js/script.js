// script.js

const tablaBody = document.querySelector("#tabla-articulos tbody");
const listaSeleccionados = document.getElementById("lista-seleccionados");
const runButton = document.getElementById("run-analysis");
const eliminarTodosBtn = document.getElementById("eliminar-todos");

// Datos de ejemplo
let articulos = [
    {id: "A1", nombre: "Artículo 1", autores: "Autor X", fecha: "2024", abstract: "Abstract 1"},
    {id: "A2", nombre: "Artículo 2", autores: "Autor Y", fecha: "2025", abstract: "Abstract 2"},
    {id: "A3", nombre: "Artículo 3", autores: "Autor Z", fecha: "2023", abstract: "Abstract 3"}
];

let seleccionados = [];

// Renderizar tabla de artículos
function renderTabla() {
    tablaBody.innerHTML = "";
    articulos.forEach(a => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${a.id}</td><td>${a.nombre}</td><td>${a.autores}</td><td>${a.fecha}</td>`;
        tr.addEventListener("click", () => toggleSeleccion(a));
        tablaBody.appendChild(tr);
    });
}

// Agregar o quitar de la lista de seleccionados
function toggleSeleccion(articulo) {
    const index = seleccionados.findIndex(a => a.id === articulo.id);
    if (index !== -1) {
        // Quitar
        seleccionados.splice(index, 1);
    } else {
        seleccionados.push(articulo);
    }
    renderSeleccionados();
}

// Renderizar lista de seleccionados
function renderSeleccionados() {
    listaSeleccionados.innerHTML = "";
    seleccionados.forEach(a => {
        const div = document.createElement("div");
        div.className = "articulo-item";
        div.innerHTML = `<strong>${a.nombre}</strong> (${a.fecha})<br>${a.autores} <button class="eliminar">Eliminar</button>
                         <div class="articulo-detalle">${a.abstract}</div>`;
        const detalle = div.querySelector(".articulo-detalle");
        div.addEventListener("click", e => {
            if(e.target.className !== "eliminar") detalle.style.display = detalle.style.display === "block" ? "none" : "block";
        });
        div.querySelector(".eliminar").addEventListener("click", e => {
            e.stopPropagation();
            seleccionados = seleccionados.filter(item => item.id !== a.id);
            renderSeleccionados();
        });
        listaSeleccionados.appendChild(div);
    });

    runButton.disabled = seleccionados.length < 2;
}

// Eliminar todos los seleccionados
eliminarTodosBtn.addEventListener("click", () => {
    seleccionados = [];
    renderSeleccionados();
});

// Simulación de análisis de similitud textual
runButton.addEventListener("click", () => {
    const resultadosDiv = document.getElementById("resultados");
    resultadosDiv.innerHTML = "";
    // Aquí se llama a tus funciones de análisis reales
    resultadosDiv.innerHTML = seleccionados.map((a,i) => `<p>Algoritmo ${i+1}: Resultado ficticio</p>`).join("");
});

renderTabla();
renderSeleccionados();
