import tkinter as tk
from tkinter import messagebox
from zera import reset_all_users, reset_specific_user
from limite import set_user_limit

# Criação da janela principal
root = tk.Tk()
root.title("Console Admin")
root.geometry("350x400")  # Tamanho inicial

# Configurar grid para responsividade
for i in range(7):  # Total de linhas
    root.grid_rowconfigure(i, weight=1)
for j in range(2):  # Total de colunas
    root.grid_columnconfigure(j, weight=1)

# Título
title_label = tk.Label(root, text="Contadores e Limites", font=("Arial", 18, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="n")

# Botão para resetar todos os usuários
reset_all_btn = tk.Button(
    root,
    text="Resetar Todos os Usuários",
    command=lambda: reset_all_users(messagebox),
    bg="red",
    fg="white",
    font=("Arial", 12),
    height=2,
    width=25,
)
reset_all_btn.grid(row=1, column=0, columnspan=2, pady=10)

# Campo para informar o usuário
user_label = tk.Label(root, text="Usuário:", font=("Arial", 12), anchor="w")
user_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

user_input = tk.Entry(root, font=("Arial", 12))
user_input.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

# Campo para definir limite personalizado
limit_label = tk.Label(root, text="Limite:", font=("Arial", 12), anchor="w")
limit_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

limit_input = tk.Entry(root, font=("Arial", 12))
limit_input.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

# Botão para resetar usuário específico
reset_user_btn = tk.Button(
    root,
    text="Resetar Contador",
    command=lambda: reset_specific_user(user_input.get().strip(), messagebox),
    bg="blue",
    fg="white",
    font=("Arial", 12),
    height=2,
    width=25,
)
reset_user_btn.grid(row=4, column=0, columnspan=2, pady=10)

# Botão para definir limite
set_limit_btn = tk.Button(
    root,
    text="Definir Limite",
    command=lambda: set_user_limit(user_input.get().strip(), limit_input.get().strip(), messagebox),
    bg="green",
    fg="white",
    font=("Arial", 12),
    height=2,
    width=25,
)
set_limit_btn.grid(row=5, column=0, columnspan=2, pady=10)

# Rodapé
footer_label = tk.Label(root, text="© 2025 - Sistema de Reset e Limites", font=("Arial", 10))
footer_label.grid(row=6, column=0, columnspan=2, pady=10, sticky="s")

# Executar a interface
root.mainloop()
