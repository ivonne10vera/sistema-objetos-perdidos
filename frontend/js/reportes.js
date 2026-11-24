let chartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    cargarReportes();
});
async function cargarReportes() {
    const alerta = document.getElementById('alertaError');
    alerta.classList.add('d-none');
    try {
        const respuesta = await fetch('http://localhost:5000/api/reportes/');
        if (!respuesta.ok) throw new Error('Error al obtener datos del servidor');

        const datos = await respuesta.json();

        // 1. Actualizar tarjetas de resumen
        document.getElementById('totalRecuperados').textContent = datos.recuperados.length;
        document.getElementById('totalPendientes').textContent = datos.pendientes.length;

        if (datos.lugares.length > 0) {
            document.getElementById('lugarTop').textContent = datos.lugares[0].lugar;
            document.getElementById('cantidadLugarTop').textContent = `${datos.lugares[0].cantidad_reportes} reportes registrados`;
        } else {
            document.getElementById('lugarTop').textContent = 'Sin datos';
            document.getElementById('cantidadLugarTop').textContent = '0 reportes';
        }

// 2. Llenar tabla de Lugares
        const tbodyLugares = document.getElementById('tablaLugares');
        if (datos.lugares.length === 0) {
            tbodyLugares.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No hay lugares registrados</td></tr>';
        } else {
            tbodyLugares.innerHTML = datos.lugares.map((item, index) => `
                <tr>
                    <td class="fw-bold">${index + 1}</td>
                    <td>${item.lugar}</td>
                    <td class="text-end"><span class="badge bg-primary rounded-pill">${item.cantidad_reportes}</span></td>
                </tr>
            `).join('');
        }
// 3. Llenar tabla de Objetos Recuperados
        const tbodyRecuperados = document.getElementById('tablaRecuperados');
        if (datos.recuperados.length === 0) {
            tbodyRecuperados.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No hay objetos recuperados</td></tr>';
        } else {
            tbodyRecuperados.innerHTML = datos.recuperados.map(obj => `
                <tr>
                    <td class="fw-semibold">${obj.titulo}</td>
                    <td>${obj.categoria}</td>
                    <td>${obj.lugar}</td>
                    <td>${formatearFecha(obj.fecha)}</td>
                </tr>
            `).join('');
        }
// 4. Llenar tabla de Objetos Pendientes
        const tbodyPendientes = document.getElementById('tablaPendientes');
        if (datos.pendientes.length === 0) {
            tbodyPendientes.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No hay objetos pendientes</td></tr>';
        } else {
            tbodyPendientes.innerHTML = datos.pendientes.map(obj => `
                <tr>
                    <td class="fw-semibold">${obj.titulo}</td>
                    <td>${obj.lugar}</td>
                    <td>${formatearFecha(obj.fecha)}</td>
                    <td>${obtenerBadgeEstado(obj.estado)}</td>
                </tr>
            `).join('');
        }
// 5. Renderizar gráfico de barras
        renderizarGrafico(datos.lugares);

    } catch (error) {
        alerta.textContent = 'No se pudo conectar con el servidor backend. Verifica que py app.py esté encendido.';
        alerta.classList.remove('d-none');
        console.error(error);
    }
}
function formatearFecha(fechaStr) {
    if (!fechaStr) return '-';
    const fecha = new Date(fechaStr);
    return fecha.toLocaleDateString('es-ES');
}
function obtenerBadgeEstado(estado) {
    const colores = {
        'reportado': 'bg-danger',
        'encontrado': 'bg-info text-dark',
        'reclamado': 'bg-warning text-dark'
    };
    const clase = colores[estado] || 'bg-secondary';
    return `<span class="badge ${clase} text-uppercase">${estado}</span>`;
}
function renderizarGrafico(lugares) {
    if (typeof Chart === 'undefined') return; // Evita error si no hay internet
    const ctx = document.getElementById('graficoLugares').getContext('2d');
    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: lugares.map(l => l.lugar),
            datasets: [{
                label: 'Cantidad de reportes',
                data: lugares.map(l => l.cantidad_reportes),
                backgroundColor: '#0d6efd',
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
        }
    });
}
