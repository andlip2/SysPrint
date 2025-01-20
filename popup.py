import tkinter as tk
from tkinter import messagebox

class Popup:
    def __init__(titulo, mensagem):
        titulo = titulo
        mensagem = mensagem

    def mostrar(titulo, mensagem):
        # Criando uma nova janela para a notificação
        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal

        # Exibindo a caixa de mensagem
        messagebox.showinfo(titulo, mensagem)

        # Fecha a janela após exibir a mensagem
        root.quit()
