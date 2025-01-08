import tkinter as tk
from tkinter import messagebox

class Popup:
    def __init__(self, titulo, mensagem):
        self.titulo = titulo
        self.mensagem = mensagem

    def mostrar(self):
        # Criando uma nova janela para a notificação
        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal

        # Exibindo a caixa de mensagem
        messagebox.showinfo(self.titulo, self.mensagem)

        # Fecha a janela após exibir a mensagem
        root.quit()
