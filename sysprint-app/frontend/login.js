async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");

    try {
        const response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();
        if (data.sucess) {
            message.style.color = "green";
            message.textContent = "Login bem-sucedido!";
            // Redireciona para a tela principal
            setTimeout(() => {
                window.location.href = "dashboard.html"; // Redireciona para a tela principal
            }, 1000); // Pequena espera antes do redirecionamento
        } else {
            message.style.color = "red";
            message.textContent = "Usuário ou senha incorretos";
        }
    } catch (error) {
        message.style.color = "red";
        message.textContent = "Erro ao conectar ao servidor";
    }
}
