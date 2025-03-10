async function fetchUsersData() {
    try {
        const response = await fetch("http://127.0.0.1:5000/users-data");
        const data = await response.json();
        console.log("Dados recebidos:", data);  // Verificar se os dados estão corretos
        renderUsersTable(data);
    } catch (error) {
        console.error("Erro ao carregar os dados da tabela de usuários:", error);
    }
}

function renderUsersTable(data) {
    const tableBody = document.querySelector("#users-table tbody");
    tableBody.innerHTML = ''; // Limpa o tbody antes de adicionar os dados

    data.forEach(user => {
        const row = tableBody.insertRow();
        row.insertCell(0).textContent = user.user;
        row.insertCell(1).textContent = user.total_pages;
        row.insertCell(2).textContent = user.print_limit;
        row.insertCell(3).textContent = user.blocked ? 'Sim' : 'Não';
        row.insertCell(4).textContent = user.department;
    });
}

// Garantir que a função é chamada quando a página carregar
window.onload = fetchUsersData;
