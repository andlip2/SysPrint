async function fetchDatabaseTables() {
    try {
        const response = await fetch("http://127.0.0.1:5000/dashboard-data");
        const data = await response.json(); 
        console.log(data);

        renderBarChart(data);
    } catch (error) {
        console.error("Erro ao carregar dados do dashboard", error);
    }
}

function renderBarChart(data) {
    const tableBody = document.querySelector(.'styled-table tbody')

    tableBody.innerHTML = ''

    data.tables.forEach(table => {
        // Linhas
        const row = document.createElement('tr');

        // Células
        const tableCell = document.createElement('td');
        tableCell.textContent = table.name;

        const descriptionCell = document.createElement('td');
        descriptionCell.textContent = table.description;

        // Adição de células nas linhas
        row.appendChild(tableCell);
        row.appendChild(descriptionCell);

        // Adição de linha ao corpo da tabela
        tableBody.appendChild(row);
    });
}

fetchDatabaseTables();