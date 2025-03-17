// Dropdown (troca de tabelas)
function changeTable() {
    const tableSelect = document.getElementById("table-select");
    const selectedTable = tableSelect.value;

    console.log("Tabela selecionada:", selectedTable);

    // Esconde todas as tabelas para que o dropdown funcione
    document.getElementById("users-table-container").style.display = "none";
    document.getElementById("logs-table-container").style.display = "none";
    document.getElementById("printers-table-container").style.display = "none";
    document.getElementById("departments-table-container").style.display = "none";
    document.getElementById("scans-table-container").style.display = "none";

    // Mostra apenas a tabela selecionada
    if (selectedTable === "users") {
        document.getElementById("users-table-container").style.display = "block";
        fetchUsersData(); // Carrega os dados da tabela de usuários
    } else if (selectedTable === "logs") {
        document.getElementById("logs-table-container").style.display = "block";
        fetchLogsData(); // Carrega os dados da tabela de logs
    } else if (selectedTable === "printers") {
        document.getElementById("printers-table-container").style.display = "block";
        fetchPrintersData();
    } else if (selectedTable === "departments") {
        document.getElementById("departments-table-container").style.display = "block";
        fetchDepartmentsData();
    } else if (selectedTable === "scans") {
        document.getElementById("scans-table-container").style.display = "block";
        fetchScansData();
    }
}


// Tabela de usuários
async function fetchUsersData() {
    try {
        const response = await fetch("http://127.0.0.1:5000/users-data");
        const data = await response.json();
        console.log("Dados recebidos:", data);
        renderUsersTable(data);
    } catch (error) {
        console.error("Erro ao carregar os dados da tabela de usuários:", error);
    }
}

function renderUsersTable(data) {
    const tableBody = document.querySelector("#users-table tbody");
    tableBody.innerHTML = '';

    data.forEach(user => {
        const row = tableBody.insertRow();
        row.insertCell(0).textContent = user.user;
        row.insertCell(1).textContent = user.total_pages;
        row.insertCell(2).textContent = user.print_limit;
        row.insertCell(3).textContent = user.blocked ? 'Sim' : 'Não';
        row.insertCell(4).textContent = user.department;
    });
}


// Tabela de logs
async function fetchLogsData() {
    try {
        const response = await fetch("http://127.0.0.1:5000/logs-data");
        const data = await response.json();
        console.log("Dados recebidos:", data);
        renderLogsTable(data);
    } catch (error) {
        console.error("Erro ao carregar os dados da tabela de logs:", error);
    }
}

function renderLogsTable(data) {
    const tableBody = document.querySelector("#logs-table tbody");
    tableBody.innerHTML = '';

    data.forEach(logs => {
        const row = tableBody.insertRow();
        row.insertCell(0).textContent = logs.time;
        row.insertCell(1).textContent = logs.user;
        row.insertCell(2).textContent = logs.pages;
        row.insertCell(3).textContent = logs.copies;
        row.insertCell(4).textContent = logs.printer;
        row.insertCell(5).textContent = logs.documentname;
        row.insertCell(6).textContent = logs.client;
        row.insertCell(7).textContent = logs.papersize;
        row.insertCell(8).textContent = logs.language;
        row.insertCell(9).textContent = logs.duplex;
        row.insertCell(10).textContent = logs.grayscale;
        row.insertCell(11).textContent = logs.size;
    });
}


// Tabela de impressoras
async function fetchPrintersData() {
    try {
        const response = await fetch("http://127.0.0.1:5000/printers-data")
        const data = await response.json();
        console.log("Dados recebidos:", data);
        renderPrintersTable(data);
    } catch (error) {
        console.error("Erro ao carregar os dados da tabela de impressoras:", error);
    }
}

function renderPrintersTable(data) {
    const tableBody = document.querySelector("#printers-table tbody")
    tableBody.innerHTML = '';

    data.forEach(printers => {
        const row = tableBody.insertRow();
        row.insertCell(0).textContent = printers.id_impressora;
        row.insertCell(1).textContent = printers.num_serie;
        row.insertCell(2).textContent = printers.modelo;
        row.insertCell(3).textContent = printers.departamento;
    });
}


// Tabela de departamentos
async function fetchDepartmentsData() {
    try {
        const response = await fetch("http://127.0.0.1:5000/departments-data")
        const data = await response.json();
        console.log("Dados recebidos:", data);
        renderDepartmentsTable(data);
    } catch (error) {
        console.error("Erro ao carregar os dados da tabela de departamentos:", error);
    }
}

function renderDepartmentsTable(data) {
    const tableBody = document.querySelector("#departments-table tbody")
    tableBody.innerHTML = '';

    data.forEach(departments => {
        const row = tableBody.insertRow();
        row.insertCell(0).textContent = departments.id_departamento;
        row.insertCell(1).textContent = departments.nome;
    });
}

// Tabela de scans
async function fetchScansData() {
    try {
        const response = await fetch("http://127.0.0.1:5000/scans-data")
        const data = await response.json();
        console.log("Dados recebidos:", data);
        renderScansTable(data);
    } catch (error) {
        console.error("Erro ao carregar os dados da tabela de scans:", error);
    }
}

function renderScansTable(data) {
    const tableBody = document.querySelector("#scans-table tbody")
    tableBody.innerHTML = '';

    data.forEach(scans => {
        const row = tableBody.insertRow();
        row.insertCell(0).textContent = scans.id_impressora;
        row.insertCell(1).textContent = scans.num_serie;
        row.insertCell(2).textContent = scans.modelo;
        row.insertCell(3).textContent = scans.copias;
        row.insertCell(4).textContent = scans.impressoes;
    });
}


window.onload = () => {
    changeTable();
};
