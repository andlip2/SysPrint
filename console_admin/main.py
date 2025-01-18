from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QGridLayout,
    QRadioButton,
)
from PyQt5.QtCore import Qt
from zera import reset_all_users, reset_specific_user
from limite import set_user_limit

class AdminConsole(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Console Admin")
        self.setGeometry(100, 100, 350, 400)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)  # Espaçamento entre widgets

        # Título
        title_label = QLabel("Contadores e Limites")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Grid para os campos de entrada e labels
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)

        # Campo para informar o usuário
        user_label = QLabel("Usuário:")
        user_label.setStyleSheet("font-size: 12px;")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Digite o usuário")
        self.user_input.setStyleSheet(
            "padding: 5px; border-radius: 12px;"  # Adicionando bordas arredondadas
        )
        form_layout.addWidget(user_label, 0, 0)
        form_layout.addWidget(self.user_input, 0, 1)

        # Campo para definir limite personalizado
        limit_label = QLabel("Limite:")
        limit_label.setStyleSheet("font-size: 12px;")
        self.limit_input = QLineEdit()
        self.limit_input.setPlaceholderText("Digite o limite")
        self.limit_input.setStyleSheet(
            "padding: 5px; border-radius: 12px;"  # Adicionando bordas arredondadas
        )
        form_layout.addWidget(limit_label, 1, 0)
        form_layout.addWidget(self.limit_input, 1, 1)

        main_layout.addLayout(form_layout)

        # Divisor para separar funções
        divider_label = QLabel("Funções")
        divider_label.setStyleSheet("font-size: 14px; font-weight: bold; text-align: center; padding: 10px;")
        main_layout.addWidget(divider_label)

        # Radio buttons para ações
        self.radio_reset_all = QRadioButton("Resetar todos os usuários")
        self.radio_reset_user = QRadioButton("Resetar contador do usuário")
        self.radio_set_limit = QRadioButton("Definir limite do usuário")

        # Agrupar os radio buttons para garantir que apenas um pode ser selecionado
        self.radio_group = [self.radio_reset_all, self.radio_reset_user, self.radio_set_limit]
        for radio in self.radio_group:
            radio.setStyleSheet("font-size: 12px;")
            radio.toggled.connect(self.update_fields_state)  # Conectar ao evento de mudança de estado
            main_layout.addWidget(radio)

        # Botão para executar ação com base na opção selecionada
        execute_btn = QPushButton("Executar Ação")
        execute_btn.setStyleSheet(
            """
            QPushButton {
                background-color: orange;
                color: white;
                font-size: 12px;
                padding: 8px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: darkorange;
            }
            """
        )
        execute_btn.clicked.connect(self.execute_action)
        main_layout.addWidget(execute_btn)

        # Rodapé
        footer_label = QLabel("© 2025 - Sistema de Reset e Limites")
        footer_label.setStyleSheet("font-size: 10px; text-align: center;")
        footer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer_label)

        self.setLayout(main_layout)

        # Inicializa o comportamento dos campos
        self.update_fields_state()

    def update_fields_state(self):
        # Desabilita/abilita os campos de acordo com a opção selecionada
        if self.radio_reset_all.isChecked():
            self.user_input.setEnabled(False)
            self.limit_input.setEnabled(False)
            self.user_input.setStyleSheet("padding: 5px; border-radius: 12px; background-color: #D3D3D3;")  # Cinza
            self.limit_input.setStyleSheet("padding: 5px; border-radius: 12px; background-color: #D3D3D3;")  # Cinza
        elif self.radio_reset_user.isChecked():
            self.user_input.setEnabled(True)
            self.limit_input.setEnabled(False)
            self.user_input.setStyleSheet("padding: 5px; border-radius: 12px;")  # Branco
            self.limit_input.setStyleSheet("padding: 5px; border-radius: 12px; background-color: #D3D3D3;")  # Cinza
        elif self.radio_set_limit.isChecked():
            self.user_input.setEnabled(True)
            self.limit_input.setEnabled(True)
            self.user_input.setStyleSheet("padding: 5px; border-radius: 12px;")  # Branco
            self.limit_input.setStyleSheet("padding: 5px; border-radius: 12px;")  # Branco

    def execute_action(self):
        # Verifica qual radio button foi selecionado
        user = self.user_input.text().strip()
        limit = self.limit_input.text().strip()

        if self.radio_reset_all.isChecked():
            result = QMessageBox.question(
                self, "Confirmação", "Deseja resetar todos os usuários?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if result == QMessageBox.Yes:
                reset_all_users()
                QMessageBox.information(self, "Sucesso", "Todos os usuários foram resetados.")

        elif self.radio_reset_user.isChecked():
            if not user:
                QMessageBox.warning(self, "Erro", "Por favor, informe um usuário.")
                return
            reset_specific_user(user)
            QMessageBox.information(self, "Sucesso", f"O contador do usuário {user} foi resetado.")

        elif self.radio_set_limit.isChecked():
            if not user or not limit:
                QMessageBox.warning(self, "Erro", "Por favor, informe o usuário e o limite.")
                return
            set_user_limit(user, limit, QMessageBox)
            QMessageBox.information(self, "Sucesso", f"O limite do usuário {user} foi definido para {limit}.")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = AdminConsole()
    window.show()
    sys.exit(app.exec_())
