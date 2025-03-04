async function fetchUsersData() {
    try {
        const response = await fetch("http://127.0.0.1:5000/get-users");
        const data = await response.json();  // Dados que vêm com as chaves 'id', 'name' e 'email'
        renderUsersTable(data);
    } catch (error) {
        console.error("Erro ao carregar os dados da tabela de usuários:", error);
    }
}

function renderUsersTable(data) {
    const table = document.getElementById('users');
    table.innerHTML = '';  // Limpa a tabela antes de adicionar os novos dados

    data.forEach(users => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${users.User}</td>   <!-- Exibindo a coluna id -->
        `;
        table.appendChild(row);  // Adiciona a linha na tabela
    });
}
