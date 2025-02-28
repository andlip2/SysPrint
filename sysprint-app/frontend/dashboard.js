// Função para buscar os dados do backend
async function fetchData() {
    try {
        // Fazendo uma requisição GET para buscar os dados do dashboard
        const response = await fetch("http://127.0.0.1:5000/dashboard-data");
        const data = await response.json(); // Convertendo a resposta para JSON

        // Exibindo os dados no console para verificar o que foi retornado
        console.log(data);

        // Chamando a função para renderizar o gráfico com os dados
        renderBarChart(data);
    } catch (error) {
        // Caso ocorra algum erro na requisição
        console.error("Erro ao carregar dados do dashboard", error);
    }
}

// Função para renderizar o gráfico com os dados
function renderBarChart(data) {
    // Pegando o contexto do canvas onde o gráfico será desenhado
    const ctx = document.getElementById('impressionsChart').getContext('2d');

    // Criando o gráfico
    const impressionsChart = new Chart(ctx, {
        type: 'bar', // Tipo de gráfico (pode ser 'bar', 'line', etc.)
        data: {
            labels: data.months, // Usando os meses retornados do backend
            datasets: [{
                label: 'Impressões por mês', // Título do gráfico
                data: data.impressions, // Usando os dados de impressões
                backgroundColor: 'rgba(54, 162, 235, 0.1)', // Cor de fundo das barras
                borderColor: 'rgba(54, 162, 235, 1)', // Cor das bordas das barras
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true // Faz o gráfico começar a escala do eixo Y do zero
                }
            }
        }
    });
    impressionsChart.resize();
}

// Função para buscar os dados do backend (impressões por setor)
async function fetchSectorData() {
    try {
        // Fazendo uma requisição GET para buscar os dados dos setores
        const response = await fetch("http://127.0.0.1:5000/sector-data");
        const data = await response.json(); // Convertendo a resposta para JSON

        // Exibindo os dados no console para verificar o que foi retornado
        console.log(data);

        // Chamando a função para renderizar o gráfico de barras horizontais com os dados
        renderBarChartHorizontal(data);
    } catch (error) {
        // Caso ocorra algum erro na requisição
        console.error("Erro ao carregar dados dos setores", error);
    }
}

// Função para renderizar o gráfico de barras horizontais com os dados
function renderBarChartHorizontal(data) {
    // Pegando o contexto do canvas onde o gráfico será desenhado
    const ctx = document.getElementById('sectorChart').getContext('2d');

    // Criando o gráfico de barras horizontais
    const sectorChart = new Chart(ctx, {
        type: 'bar', // Tipo de gráfico (bar para gráfico de barras)
        data: {
            labels: data.sectors, // Usando os setores retornados do backend
            datasets: [{
                label: 'Impressões por setor', // Título do gráfico
                data: data.impressions, // Usando os dados de impressões
                backgroundColor: [
                    'rgba(255, 99, 132, 0.1)', // Cor para o primeiro setor
                    'rgba(54, 162, 235, 0.1)', // Cor para o segundo setor
                    'rgba(255, 206, 86, 0.1)', // Cor para o terceiro setor
                    'rgba(75, 192, 192, 0.1)', // Cor para o quarto setor
                    'rgba(153, 102, 255, 0.1)', // Cor para o quinto setor
                    'rgba(255, 159, 64, 0.1)'  // Cor para o sexto setor
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)', // Cor de borda para o primeiro setor
                    'rgba(54, 162, 235, 1)', // Cor de borda para o segundo setor
                    'rgba(255, 206, 86, 1)', // Cor de borda para o terceiro setor
                    'rgba(75, 192, 192, 1)', // Cor de borda para o quarto setor
                    'rgba(153, 102, 255, 1)', // Cor de borda para o quinto setor
                    'rgba(255, 159, 64, 1)'  // Cor de borda para o sexto setor
                ],
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y', // Altera a direção do gráfico para horizontal
            scales: {
                x: {
                    beginAtZero: true // Garante que o eixo X comece do zero
                }
            }
        }
    });
    sectorChart.resize();
}

// Função de logout (caso queira fazer o logout da aplicação)
function logout() {
    window.location.href = "login.html"; // Redireciona para a página de login
}

// Chamando as funções para carregar os dados e renderizar os gráficos assim que a página carregar
fetchData(); // Gráfico de barras
fetchSectorData(); // Gráfico de pizza
