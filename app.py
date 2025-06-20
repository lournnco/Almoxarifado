import sys
import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QListWidget, QRadioButton, QMessageBox
)
from PyQt6.QtGui import QPixmap
from datetime import datetime
from pytz import timezone


DB_NAME = "almox"
DB_USER = "root"
DB_PASSWORD = "manulauro5308"
DB_HOST = "localhost"
DB_PORT = 3306


class AlmoxarifadoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Almoxarifado - Liberato")
        self.showMaximized()

        main_layout = QGridLayout()

        self.criar_grupo_detalhes()
        self.criar_grupo_pesquisa()
        self.criar_grupo_pesquisa_componente()
        self.criar_grupo_emprestimos()

        main_layout.addWidget(self.group_detalhes, 0, 0)
        main_layout.addWidget(self.group_pesquisa, 0, 1)
        main_layout.addWidget(self.group_pesquisa_componente, 1, 0, 1, 2)
        main_layout.addWidget(self.group_emprestimos, 2, 0, 1, 2)

        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 3)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)

        self.setLayout(main_layout)
        self.matricula_selecionada = None

    # 🔸 Grupo Detalhes Aluno
    def criar_grupo_detalhes(self):
        self.group_detalhes = QGroupBox("Detalhes do Aluno")
        layout = QHBoxLayout()

        self.foto_label = QLabel()
        self.foto_label.setPixmap(QPixmap("default.png").scaled(100, 100))
        self.foto_label.setFixedSize(100, 100)
        layout.addWidget(self.foto_label)

        info = QVBoxLayout()
        self.label_matricula = QLabel("Matrícula: -")
        self.label_nome = QLabel("Nome: -")
        self.label_email = QLabel("E-mail: -")
        self.label_turma = QLabel("Turma: -")
        info.addWidget(self.label_matricula)
        info.addWidget(self.label_nome)
        info.addWidget(self.label_email)
        info.addWidget(self.label_turma)

        layout.addLayout(info)
        self.group_detalhes.setLayout(layout)

    # 🔸 Grupo Pesquisa Aluno
    def criar_grupo_pesquisa(self):
        self.group_pesquisa = QGroupBox("Pesquisar Aluno")
        layout = QVBoxLayout()

        self.pesquisa_input = QLineEdit()
        self.pesquisa_input.setPlaceholderText("Digite matrícula ou nome")
        layout.addWidget(self.pesquisa_input)

        self.botao_pesquisa = QPushButton("Pesquisar")
        self.botao_pesquisa.clicked.connect(self.pesquisar_aluno)
        layout.addWidget(self.botao_pesquisa)

        self.lista_alunos = QListWidget()
        self.lista_alunos.itemClicked.connect(self.mostrar_detalhes_aluno)
        layout.addWidget(self.lista_alunos)

        self.group_pesquisa.setLayout(layout)

    # 🔸 Grupo Pesquisa Componente
    def criar_grupo_pesquisa_componente(self):
        self.group_pesquisa_componente = QGroupBox("Pesquisar Componente")
        layout = QVBoxLayout()

        self.pesquisa_componente_input = QLineEdit()
        self.pesquisa_componente_input.setPlaceholderText(
            "Digite nome ou código do componente"
        )
        layout.addWidget(self.pesquisa_componente_input)

        tipo_layout = QHBoxLayout()
        self.radio_nome = QRadioButton("Por Nome")
        self.radio_nome.setChecked(True)
        self.radio_codigo = QRadioButton("Por Código")
        tipo_layout.addWidget(self.radio_nome)
        tipo_layout.addWidget(self.radio_codigo)
        layout.addLayout(tipo_layout)

        self.botao_pesquisa_componente = QPushButton("Buscar Componente")
        self.botao_pesquisa_componente.clicked.connect(
            self.pesquisar_componente
        )
        layout.addWidget(self.botao_pesquisa_componente)

        self.lista_componentes = QListWidget()
        self.lista_componentes.itemDoubleClicked.connect(
            self.selecionar_componente
        )
        layout.addWidget(self.lista_componentes)

        self.group_pesquisa_componente.setLayout(layout)

    # 🔸 Grupo Empréstimos
    def criar_grupo_emprestimos(self):
        self.group_emprestimos = QGroupBox("Lista de Empréstimos")
        layout = QVBoxLayout()

        self.tabela_emprestimos = QTableWidget()
        self.tabela_emprestimos.setColumnCount(5)
        self.tabela_emprestimos.setHorizontalHeaderLabels(
            ["Quantidade", "Código", "Nome", "Retirada", "Devolução"]
        )
        layout.addWidget(self.tabela_emprestimos)

        form = QHBoxLayout()
        self.input_componente = QLineEdit()
        self.input_componente.setPlaceholderText("ID ou nome do componente")
        self.input_quantidade = QLineEdit()
        self.input_quantidade.setPlaceholderText("Quantidade")
        self.botao_adicionar = QPushButton("Adicionar Empréstimo")
        self.botao_adicionar.clicked.connect(self.adicionar_emprestimo)
        form.addWidget(self.input_componente)
        form.addWidget(self.input_quantidade)
        form.addWidget(self.botao_adicionar)
        layout.addLayout(form)

        self.botao_devolver = QPushButton("Registrar Devolução")
        self.botao_devolver.clicked.connect(self.registrar_devolucao)
        layout.addWidget(self.botao_devolver)

        self.group_emprestimos.setLayout(layout)

    # 🔍 Pesquisa Aluno
    def pesquisar_aluno(self):
        termo = self.pesquisa_input.text().strip()
        self.lista_alunos.clear()

        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            cursor.execute(
                "SELECT matricula, nome FROM alunos "
                "WHERE matricula LIKE %s OR nome LIKE %s",
                (f"%{termo}%", f"%{termo}%")
            )
            resultados = cursor.fetchall()

            if resultados:
                for mat, nome in resultados:
                    self.lista_alunos.addItem(f"{mat} - {nome}")
            else:
                self.lista_alunos.addItem("Nenhum aluno encontrado.")

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Erro", f"Erro na pesquisa: {e}")

    # 📄 Mostrar Detalhes Aluno + Carregar Empréstimos
    def mostrar_detalhes_aluno(self, item):
        matricula = item.text().split(" - ")[0]
        self.matricula_selecionada = matricula

        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            cursor.execute(
                "SELECT nome, email, turma, foto "
                "FROM alunos WHERE matricula = %s",
                (matricula,)
            )
            aluno = cursor.fetchone()

            if aluno:
                nome, email, turma, foto_bytes = aluno
                self.label_matricula.setText(f"Matrícula: {matricula}")
                self.label_nome.setText(f"Nome: {nome}")
                self.label_email.setText(f"E-mail: {email}")
                self.label_turma.setText(f"Turma: {turma}")

                # Carregar foto
                if foto_bytes:
                    pixmap = QPixmap()
                    pixmap.loadFromData(foto_bytes)
                    pixmap = pixmap.scaled(
                        self.foto_label.width(), self.foto_label.height()
                    )
                    self.foto_label.setPixmap(pixmap)
                else:
                    # Sem foto, usa imagem padrão
                    self.foto_label.setPixmap(
                        QPixmap("default.png").scaled(
                            self.foto_label.width(), self.foto_label.height()
                        )
                    )

                self.carregar_emprestimos(matricula)

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar aluno: {e}")

    # 🔍 Pesquisa Componente
    def pesquisar_componente(self):
        termo = self.pesquisa_componente_input.text().strip()
        self.lista_componentes.clear()

        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            if self.radio_nome.isChecked():
                cursor.execute(
                    "SELECT id, nome FROM componentes WHERE nome LIKE %s",
                    (f"%{termo}%",)
                )
            else:
                cursor.execute(
                    "SELECT id, nome FROM componentes WHERE id = %s",
                    (termo,)
                )

            resultados = cursor.fetchall()

            if resultados:
                for cid, nome in resultados:
                    self.lista_componentes.addItem(
                        f"{cid} - {nome}"
                    )
            else:
                self.lista_componentes.addItem(
                    "Nenhum componente encontrado."
                )

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Erro", f"Erro na pesquisa: {e}")

    # 🎯 Selecionar componente
    def selecionar_componente(self, item):
        texto = item.text()
        id_comp = texto.split(" - ")[0]
        self.input_componente.setText(id_comp)
        self.input_quantidade.setFocus()

    # 🔄 Carregar Empréstimos
    def carregar_emprestimos(self, matricula):
        self.tabela_emprestimos.setRowCount(0)

        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            cursor.execute(
                """SELECT e.quantidade, c.id, c.nome,
                   e.data_emprestimo, e.data_devolucao
                   FROM emprestimos e
                   JOIN alunos a ON e.aluno_id = a.id
                   JOIN componentes c ON e.componente_id = c.id
                   WHERE a.matricula = %s""",
                (matricula,)
            )

            registros = cursor.fetchall()
            for row, (qtd, cid, nome, data_emp, data_dev) in enumerate(
                registros
            ):
                self.tabela_emprestimos.insertRow(row)
                self.tabela_emprestimos.setItem(
                    row, 0, QTableWidgetItem(str(qtd))
                )
                self.tabela_emprestimos.setItem(
                    row, 1, QTableWidgetItem(str(cid))
                )
                self.tabela_emprestimos.setItem(
                    row, 2, QTableWidgetItem(nome)
                )
                self.tabela_emprestimos.setItem(
                    row, 3, QTableWidgetItem(str(data_emp))
                )
                self.tabela_emprestimos.setItem(
                    row, 4,
                    QTableWidgetItem(str(data_dev) if data_dev else "")
                )

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao carregar empréstimos: {e}"
            )

    # ➕ Adicionar Empréstimo
    def adicionar_emprestimo(self):
        if not self.matricula_selecionada:
            QMessageBox.warning(self, "Aviso", "Selecione um aluno.")
            return

        comp = self.input_componente.text().strip()
        qtd = self.input_quantidade.text().strip()

        if not comp or not qtd.isdigit():
            QMessageBox.warning(
                self, "Aviso", "Preencha corretamente os dados."
            )
            return

        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM alunos WHERE matricula = %s",
                (self.matricula_selecionada,)
            )
            aluno_id = cursor.fetchone()[0]

            cursor.execute(
                "SELECT id FROM componentes "
                "WHERE id = %s OR nome LIKE %s",
                (comp, f"%{comp}%")
            )
            comp_data = cursor.fetchone()

            if not comp_data:
                QMessageBox.warning(
                    self, "Aviso", "Componente não encontrado."
                )
                return

            comp_id = comp_data[0]

            agora = datetime.now(timezone("America/Sao_Paulo"))

            cursor.execute(
                """INSERT INTO emprestimos (
                    aluno_id, componente_id, quantidade, data_emprestimo
                ) VALUES (%s, %s, %s, %s)""",
                (aluno_id, comp_id, int(qtd), agora.date())
            )

            conn.commit()
            self.carregar_emprestimos(self.matricula_selecionada)
            QMessageBox.information(
                self, "Sucesso", "Empréstimo registrado!"
            )

            self.input_componente.clear()
            self.input_quantidade.clear()

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Erro", f"Erro: {e}")

    # 🔁 Registrar Devolução
    def registrar_devolucao(self):
        linha = self.tabela_emprestimos.currentRow()
        if linha < 0:
            QMessageBox.warning(
                self, "Aviso", "Selecione um empréstimo."
            )
            return

        cod = self.tabela_emprestimos.item(linha, 1).text()

        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            cursor.execute(
                """UPDATE emprestimos SET data_devolucao = %s
                   WHERE componente_id = %s
                   AND aluno_id = (
                       SELECT id FROM alunos WHERE matricula = %s
                   )
                   AND data_devolucao IS NULL""",
                (datetime.now(timezone("America/Sao_Paulo")).date(),
                 cod, self.matricula_selecionada)
            )

            conn.commit()
            self.carregar_emprestimos(self.matricula_selecionada)
            QMessageBox.information(
                self, "Sucesso", "Devolução registrada!"
            )

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Erro", f"Erro: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlmoxarifadoApp()
    window.show()
    sys.exit(app.exec())
