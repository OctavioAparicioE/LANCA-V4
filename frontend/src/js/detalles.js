document.addEventListener("DOMContentLoaded", function() {
    let page = 1;
    let loading = false;
    const tableBody = document.getElementById("table-body");
    const tableContainer = document.getElementById("table-container");
    const loadingIndicator = document.getElementById("loading");
    const id = document.getElementById("id").value; // Asegúrate de que el id esté disponible en el HTML

    const loadMoreData = async () => {
        if (loading) return;
        loading = true;
        loadingIndicator.style.display = 'block';
        
        try {
            const response = await fetch(`/detalles_data?id=${id}&page=${page}`);
            const data = await response.json();
            if (data.length === 0) {
                // No hay más datos para cargar
                loadingIndicator.style.display = 'none';
                return;
            }

            data.forEach(row => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${row.identificador}</td>
                    <td>${row.scan}</td>
                    <td>${row.amplitud1}</td>
                    <td>${row.fase1}</td>
                    <td>${row.amplitud2}</td>
                    <td>${row.fase2}</td>
                    <td>${row.amplitud3}</td>
                    <td>${row.fase3}</td>
                `;
                tableBody.appendChild(tr);
            });

            page++;
            loadingIndicator.style.display = 'none';
        } catch (error) {
            console.error("Error loading data", error);
        } finally {
            loading = false;
        }
    };

    tableContainer.addEventListener('scroll', () => {
        if (tableContainer.scrollTop + tableContainer.clientHeight >= tableContainer.scrollHeight) {
            loadMoreData();
        }
    });

    // Inicialmente carga algunos datos
    loadMoreData();
});
